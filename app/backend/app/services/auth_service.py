from jose import JWTError

from app.backend.app.api.errors import NotFoundError, UnauthorizedError
from app.backend.app.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from app.backend.app.repositories import user_repo
from app.backend.app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutResponse,
    TokenResponse,
)


def login(payload: LoginRequest) -> TokenResponse:
    user = user_repo.get_user_by_email(payload.email)

    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise UnauthorizedError("Invalid email or password")

    access_token = create_access_token(
        user_id=user["user_id"],
        role_name=user["role_name"],
    )

    return TokenResponse(
        access_token=access_token,
        user=AuthenticatedUser(
            user_id=user["user_id"],
            name=user["name"],
            email=user["email"],
            role_name=user["role_name"],
        ),
    )


def get_current_user(token: str | None) -> AuthenticatedUser:
    if not token:
        raise UnauthorizedError("Missing bearer token")

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid bearer token") from exc

    user = user_repo.get_user_by_id(user_id)

    if user is None:
        raise NotFoundError("Authenticated user was not found")

    return AuthenticatedUser(
        user_id=user["user_id"],
        name=user["name"],
        email=user["email"],
        role_name=user["role_name"],
    )


def logout() -> LogoutResponse:
    return LogoutResponse(message="Logged out")
