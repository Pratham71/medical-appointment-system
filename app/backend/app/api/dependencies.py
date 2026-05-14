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
    token = credentials.credentials if credentials else None
    try:
        return auth_service.get_current_user(token)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


def require_roles(*allowed_roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    allowed = {role.lower() for role in allowed_roles}

    def dependency(
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AuthenticatedUser:
        if user.role_name.lower() not in allowed:
            raise service_error_to_http(ForbiddenError("Insufficient role"))
        return user

    return dependency


def require_student_id(
    user: Annotated[AuthenticatedUser, Depends(require_roles("student"))],
) -> int:
    try:
        return auth_service.get_student_id_for_user(user.user_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc


def require_doctor_staff_id(
    user: Annotated[AuthenticatedUser, Depends(require_roles("doctor"))],
) -> int:
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
) -> None:
    try:
        allowed = auth_service.can_access_appointment(
            user,
            appointment_id,
            allow_student=allow_student,
            allow_doctor=allow_doctor,
            allow_admin=allow_admin,
        )
    except Exception as exc:
        raise service_error_to_http(exc) from exc

    if not allowed:
        raise service_error_to_http(ForbiddenError("Insufficient role"))


def ensure_student_record_access(
    user: AuthenticatedUser,
    student_id: int,
) -> None:
    try:
        allowed = auth_service.can_access_student_records(user, student_id)
    except Exception as exc:
        raise service_error_to_http(exc) from exc

    if not allowed:
        raise service_error_to_http(ForbiddenError("Insufficient role"))
