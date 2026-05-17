from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.backend.app.api.errors import ForbiddenError, service_error_to_http
from app.backend.app.schemas.auth import AuthenticatedUser
from app.backend.app.services import auth_service


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:
    """FastAPI dependency that extracts and validates the JWT bearer token.

    Args:
        credentials: HTTP bearer credentials extracted by the bearer scheme,
            or None if the Authorization header is absent.

    Returns:
        The AuthenticatedUser resolved from the token.

    Raises:
        HTTPException: 401 if the token is missing or invalid; 404 if the user
            no longer exists in the database.
    """
    token = credentials.credentials if credentials else None
    try:
        return auth_service.get_current_user(token)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


def require_roles(*allowed_roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """Return a FastAPI dependency that enforces role-based access control.

    Args:
        *allowed_roles: One or more role names permitted to access the endpoint.

    Returns:
        A dependency callable that returns the authenticated user if their role
        is in the allowed set.

    Raises:
        HTTPException: 403 if the user's role is not in the allowed set.
    """
    allowed = {role.lower() for role in allowed_roles}

    def dependency(
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AuthenticatedUser:
        """Verify the authenticated user holds one of the permitted roles.

        Args:
            user: The currently authenticated user.

        Returns:
            The authenticated user if their role is allowed.

        Raises:
            HTTPException: 403 if the role is insufficient.
        """
        if user.role_name.lower() not in allowed:
            raise service_error_to_http(ForbiddenError("Insufficient role"))
        return user

    return dependency


def require_student_id(
    user: Annotated[
        AuthenticatedUser,
        Depends(
            require_roles(
                "student",
                "professor",
                "college-staff",
                "hostel-staff",
            )
        ),
    ],
) -> int:
    """FastAPI dependency that resolves the authenticated user's student_id.

    Args:
        user: The authenticated user restricted to patient roles.

    Returns:
        The integer student_id linked to the user account.

    Raises:
        HTTPException: 403 if the user has no linked student profile.
    """
    try:
        return auth_service.get_student_id_for_user(user.user_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


def require_doctor_staff_id(
    user: Annotated[AuthenticatedUser, Depends(require_roles("doctor"))],
) -> int:
    """FastAPI dependency that resolves the authenticated doctor's staff_id.

    Args:
        user: The authenticated user restricted to the "doctor" role.

    Returns:
        The integer staff_id linked to the user's doctor profile.

    Raises:
        HTTPException: 403 if the user has no linked doctor staff profile.
    """
    try:
        return auth_service.get_staff_id_for_user(user.user_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


def ensure_appointment_access(
    user: AuthenticatedUser,
    appointment_id: int,
    *,
    allow_student: bool,
    allow_doctor: bool,
    allow_admin: bool,
    allow_staff: bool = False,
) -> None:
    """Guard helper that raises HTTP 403 if the user cannot access an appointment.

    Args:
        user: The currently authenticated user.
        appointment_id: Primary key of the appointment to check.
        allow_student: Whether the owning student may access this endpoint.
        allow_doctor: Whether the assigned doctor may access this endpoint.
        allow_admin: Whether any admin may access this endpoint.
        allow_staff: Whether any staff member may access this endpoint.

    Raises:
        HTTPException: 403 if access is denied; 404 if the appointment does not exist.
    """
    try:
        allowed = auth_service.can_access_appointment(
            user,
            appointment_id,
            allow_student=allow_student,
            allow_doctor=allow_doctor,
            allow_admin=allow_admin,
            allow_staff=allow_staff,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc

    if not allowed:
        raise service_error_to_http(ForbiddenError("Insufficient role"))


def ensure_student_record_access(
    user: AuthenticatedUser,
    student_id: int,
) -> None:
    """Guard helper that raises HTTP 403 if the user cannot access a student's records.

    Args:
        user: The currently authenticated user.
        student_id: Primary key of the student whose records are being accessed.

    Raises:
        HTTPException: 403 if the user is not the student, an admin, or a doctor
            who has seen the student.
    """
    try:
        allowed = auth_service.can_access_student_records(user, student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc

    if not allowed:
        raise service_error_to_http(ForbiddenError("Insufficient role"))
