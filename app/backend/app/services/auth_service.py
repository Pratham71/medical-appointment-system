from jose import JWTError
from mysql.connector import IntegrityError

from app.backend.app.api.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServiceError,
    UnauthorizedError,
)
from app.backend.app.core.security_controls import get_login_attempt_tracker
from app.backend.app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.backend.app.core.config import get_settings
from app.backend.app.repositories import appointment_repo, doctor_repo, user_repo
from app.backend.app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutResponse,
    SignupRequest,
    TokenResponse,
)


def login(payload: LoginRequest) -> TokenResponse:
    tracker = get_login_attempt_tracker()
    settings = get_settings()
    tracker.max_attempts = settings.login_max_failed_attempts
    tracker.lockout_seconds = settings.login_lockout_seconds
    email = str(payload.email).lower()
    if tracker.is_blocked(email):
        raise RateLimitError("Too many failed login attempts")

    user = user_repo.get_user_by_email(payload.email)

    if user is None or not verify_password(payload.password, user["password_hash"]):
        tracker.record_failure(email)
        raise UnauthorizedError("Invalid email or password")

    tracker.record_success(email)
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


def signup(payload: SignupRequest) -> TokenResponse:
    try:
        user = user_repo.create_student_user(
            name=payload.name,
            email=str(payload.email).lower(),
            password_hash=hash_password(payload.password),
            roll_number=payload.roll_number,
            department=payload.department,
            year_level=payload.year_level,
        )
    except IntegrityError as exc:
        raise ConflictError("Email or roll number already exists") from exc

    if user is None:
        raise ServiceError("Student role is not configured")

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


def get_student_id_for_user(user_id: int) -> int:
    student_id = user_repo.get_student_id_by_user_id(user_id)
    if student_id is None:
        raise ForbiddenError("Authenticated user is not linked to a student")
    return student_id


def get_staff_id_for_user(user_id: int) -> int:
    staff_id = user_repo.get_staff_id_by_user_id(user_id)
    if staff_id is None:
        raise ForbiddenError("Authenticated user is not linked to a doctor")
    return staff_id


def can_access_appointment(
    user: AuthenticatedUser,
    appointment_id: int,
    *,
    allow_student: bool,
    allow_doctor: bool,
    allow_admin: bool,
) -> bool:
    role = user.role_name.lower()
    if role == "admin" and allow_admin:
        return True

    context = appointment_repo.get_access_context(appointment_id)
    if context is None:
        raise NotFoundError("Appointment was not found")

    if role in {"student", "professor"} and allow_student:
        return context["student_id"] == get_student_id_for_user(user.user_id)

    if role == "doctor" and allow_doctor:
        return context["doctor_id"] == get_staff_id_for_user(user.user_id)

    return False


def can_access_student_records(
    user: AuthenticatedUser,
    student_id: int,
) -> bool:
    role = user.role_name.lower()
    if role == "admin":
        return True
    if role in {"student", "professor"}:
        return student_id == get_student_id_for_user(user.user_id)
    if role == "doctor":
        staff_id = get_staff_id_for_user(user.user_id)
        return doctor_repo.has_doctor_seen_student(staff_id, student_id)
    return False
