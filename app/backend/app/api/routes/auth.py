from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutResponse,
    TokenResponse,
)
from app.backend.app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    try:
        return auth_service.login(payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post("/logout", response_model=LogoutResponse)
def logout() -> LogoutResponse:
    try:
        return auth_service.logout()
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/me", response_model=AuthenticatedUser)
def me(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:
    token = credentials.credentials if credentials else None
    try:
        return auth_service.get_current_user(token)
    except Exception as exc:
        raise service_error_to_http(exc) from exc
