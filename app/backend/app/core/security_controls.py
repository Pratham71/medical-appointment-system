from __future__ import annotations

import hashlib
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import Request
from starlette.responses import JSONResponse, Response

from app.backend.app.core.config import get_settings


class FixedWindowRateLimiter:
    def __init__(
        self,
        limit: int,
        window_seconds: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self._buckets: dict[str, tuple[int, float]] = {}

    def allow(self, key: str) -> bool:
        now = self.clock()
        count, reset_at = self._buckets.get(key, (0, now + self.window_seconds))

        if now >= reset_at:
            count = 0
            reset_at = now + self.window_seconds

        if count >= self.limit:
            self._buckets[key] = (count, reset_at)
            return False

        self._buckets[key] = (count + 1, reset_at)
        return True

    def reset(self) -> None:
        self._buckets.clear()


class LoginAttemptTracker:
    def __init__(
        self,
        max_attempts: int,
        lockout_seconds: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self.clock = clock
        self._attempts: dict[str, tuple[int, float]] = {}

    def is_blocked(self, email: str) -> bool:
        key = email.lower()
        count, locked_until = self._attempts.get(key, (0, 0))
        if locked_until and self.clock() >= locked_until:
            self._attempts.pop(key, None)
            return False
        return count >= self.max_attempts and locked_until > self.clock()

    def record_failure(self, email: str) -> None:
        key = email.lower()
        count, locked_until = self._attempts.get(key, (0, 0))
        if locked_until and self.clock() >= locked_until:
            count = 0
            locked_until = 0

        count += 1
        if count >= self.max_attempts:
            locked_until = self.clock() + self.lockout_seconds

        self._attempts[key] = (count, locked_until)

    def record_success(self, email: str) -> None:
        self._attempts.pop(email.lower(), None)

    def reset(self) -> None:
        self._attempts.clear()


@dataclass(frozen=True)
class IdempotencyRecord:
    signature: str
    status_code: int
    body: bytes
    headers: tuple[tuple[str, str], ...]
    expires_at: float


class IdempotencyStore:
    def __init__(
        self,
        ttl_seconds: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.clock = clock
        self._records: dict[str, IdempotencyRecord] = {}

    def get(self, key: str) -> IdempotencyRecord | None:
        record = self._records.get(key)
        if record is None:
            return None
        if self.clock() >= record.expires_at:
            self._records.pop(key, None)
            return None
        return record

    def save(
        self,
        key: str,
        signature: str,
        status_code: int,
        body: bytes,
        headers: tuple[tuple[str, str], ...],
    ) -> None:
        self._records[key] = IdempotencyRecord(
            signature=signature,
            status_code=status_code,
            body=body,
            headers=headers,
            expires_at=self.clock() + self.ttl_seconds,
        )

    def reset(self) -> None:
        self._records.clear()


_request_rate_limiter = FixedWindowRateLimiter(limit=120, window_seconds=60)
_login_attempt_tracker = LoginAttemptTracker(max_attempts=5, lockout_seconds=300)
_idempotency_store = IdempotencyStore(ttl_seconds=600)


def get_login_attempt_tracker() -> LoginAttemptTracker:
    return _login_attempt_tracker


def reset_security_state() -> None:
    _request_rate_limiter.reset()
    _login_attempt_tracker.reset()
    _idempotency_store.reset()


async def security_request_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    settings = get_settings()

    if settings.rate_limit_enabled:
        _request_rate_limiter.limit = settings.rate_limit_per_minute
        client_key = _client_key(request)
        if not _request_rate_limiter.allow(client_key):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )

    if _requires_idempotency(request):
        _idempotency_store.ttl_seconds = settings.idempotency_key_ttl_seconds
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return JSONResponse(
                status_code=400,
                content={"detail": "Idempotency-Key header is required"},
            )
        if len(idempotency_key) > 128:
            return JSONResponse(
                status_code=400,
                content={"detail": "Idempotency-Key header is too long"},
            )
        return await _handle_idempotent_request(request, call_next, idempotency_key)

    return await call_next(request)


async def _handle_idempotent_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
    idempotency_key: str,
) -> Response:
    body = await request.body()
    signature = _request_signature(request, body)
    store_key = _store_key(request, idempotency_key)
    existing = _idempotency_store.get(store_key)

    if existing is not None:
        if existing.signature != signature:
            return JSONResponse(
                status_code=409,
                content={"detail": "Idempotency key was already used"},
            )
        return Response(
            content=existing.body,
            status_code=existing.status_code,
            headers=dict(existing.headers),
        )

    response = await call_next(request)
    response_body = b"".join([chunk async for chunk in response.body_iterator])
    headers = _cacheable_headers(response)

    if response.status_code < 500:
        _idempotency_store.save(
            store_key,
            signature,
            response.status_code,
            response_body,
            headers,
        )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(headers),
        media_type=response.media_type,
    )


def _requires_idempotency(request: Request) -> bool:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False
    if request.url.path in {"/auth/login", "/auth/logout"}:
        return False
    if not request.headers.get("Authorization"):
        return False
    return True


def _client_key(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if authorization:
        return _hash_value(authorization)
    client_host = request.client.host if request.client else "unknown"
    return client_host


def _store_key(request: Request, idempotency_key: str) -> str:
    authorization = request.headers.get("Authorization", "")
    return _hash_value(f"{authorization}:{idempotency_key}")


def _request_signature(request: Request, body: bytes) -> str:
    body_hash = hashlib.sha256(body).hexdigest()
    return _hash_value(f"{request.method}:{request.url.path}:{body_hash}")


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _cacheable_headers(response: Response) -> tuple[tuple[str, str], ...]:
    excluded = {"content-length", "transfer-encoding"}
    return tuple(
        (key, value)
        for key, value in response.headers.items()
        if key.lower() not in excluded
    )
