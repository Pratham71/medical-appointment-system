from fastapi import APIRouter, Depends, status

from app.backend.app.api.dependencies import get_current_user
from app.backend.app.api.errors import service_error_to_http
from app.backend.app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutResponse,
    SignupRequest,
    TokenResponse,
)
from app.backend.app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(payload: SignupRequest) -> TokenResponse:
    """Register a new student account and return a JWT access token.

    Args:
        payload: Sign-up data including name, email, password, and student profile fields.

    Returns:
        A TokenResponse with access_token and user info on success.

    Raises:
        HTTPException: 409 if the email or roll number is already taken;
            500 for unexpected service errors.
    """
    try:
        return auth_service.signup(payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    """Authenticate a user and return a JWT access token.

    Args:
        payload: Login credentials containing email and password.

    Returns:
        A TokenResponse with access_token and user info on success.

    Raises:
        HTTPException: 429 if the account is locked out; 401 for invalid credentials.
    """
    try:
        return auth_service.login(payload)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.post("/logout", response_model=LogoutResponse)
def logout(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> LogoutResponse:
    """Invalidate the current session and return a logout confirmation.

    Args:
        current_user: The authenticated user performing the logout.

    Returns:
        A LogoutResponse with a confirmation message.
    """
    try:
        return auth_service.logout()
    except Exception as exc:
        raise service_error_to_http(exc) from exc


@router.get("/me", response_model=AuthenticatedUser)
def me(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Return the currently authenticated user's profile.

    Args:
        current_user: The authenticated user resolved from the bearer token.

    Returns:
        The AuthenticatedUser with id, name, email, and role.
    """
    return current_user
