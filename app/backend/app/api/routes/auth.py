from fastapi import APIRouter, Depends

from app.backend.app.api.dependencies import get_current_user
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutResponse,
    TokenResponse,
)
from app.backend.app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    try:
        return auth_service.login(payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post("/logout", response_model=LogoutResponse)
def logout(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> LogoutResponse:
    try:
        return auth_service.logout()
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/me", response_model=AuthenticatedUser)
def me(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    return current_user
