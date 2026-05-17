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


PATIENT_ROLES = {"student", "professor", "college-staff", "hostel-staff"}


def login(payload: LoginRequest) -> TokenResponse:
    """Authenticate a user with email and password, returning a JWT access token.

    Args:
        payload: Login credentials containing email and password.

    Returns:
        A TokenResponse with the JWT access_token and the authenticated user info.

    Raises:
        RateLimitError: If the account is currently locked out due to too many failures.
        UnauthorizedError: If the email does not exist or the password is incorrect.
    """
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
    """Register a new student account and return a JWT access token.

    Args:
        payload: Sign-up data including name, email, password, and student profile fields.

    Returns:
        A TokenResponse with the JWT access_token and the new user's info.

    Raises:
        ConflictError: If the email or roll number is already taken.
        ServiceError: If the "student" role is not configured in the database.
    """
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
    """Decode a JWT bearer token and return the authenticated user.

    Args:
        token: Raw JWT string extracted from the Authorization header, or None.

    Returns:
        An AuthenticatedUser with the user's ID, name, email, and role.

    Raises:
        UnauthorizedError: If the token is missing, invalid, or expired.
        NotFoundError: If the user referenced by the token no longer exists.
    """
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
    """Produce a logout acknowledgement response.

    Returns:
        A LogoutResponse with a confirmation message.
    """
    return LogoutResponse(message="Logged out")


def get_student_id_for_user(user_id: int) -> int:
    """Return the student_id for a user, raising if none exists.

    Args:
        user_id: Primary key of the user account.

    Returns:
        The integer student_id.

    Raises:
        ForbiddenError: If the user has no linked student profile.
    """
    student_id = user_repo.get_student_id_by_user_id(user_id)
    if student_id is None:
        raise ForbiddenError("Authenticated user is not linked to a student")
    return student_id


def get_staff_id_for_user(user_id: int) -> int:
    """Return the doctor staff_id for a user, raising if none exists.

    Args:
        user_id: Primary key of the user account.

    Returns:
        The integer staff_id.

    Raises:
        ForbiddenError: If the user has no linked doctor staff profile.
    """
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
    allow_staff: bool = False,
) -> bool:
    """Check whether a user is authorised to access a specific appointment.

    Args:
        user: The currently authenticated user.
        appointment_id: Primary key of the appointment to check.
        allow_student: Whether the owning student may access this endpoint.
        allow_doctor: Whether the assigned doctor may access this endpoint.
        allow_admin: Whether any admin may access this endpoint.
        allow_staff: Whether any staff member may access this endpoint.

    Returns:
        True if the user is authorised, False otherwise.

    Raises:
        NotFoundError: If the appointment does not exist.
        ForbiddenError: Raised indirectly via get_student_id_for_user or
            get_staff_id_for_user if the user lacks the required profile.
    """
    role = user.role_name.lower()
    if role == "admin" and allow_admin:
        return True
    if role == "staff" and allow_staff:
        return True

    context = appointment_repo.get_access_context(appointment_id)
    if context is None:
        raise NotFoundError("Appointment was not found")

    if role in PATIENT_ROLES and allow_student:
        return context["student_id"] == get_student_id_for_user(user.user_id)

    if role == "doctor" and allow_doctor:
        return context["doctor_id"] == get_staff_id_for_user(user.user_id)

    return False


def can_access_student_records(
    user: AuthenticatedUser,
    student_id: int,
) -> bool:
    """Check whether a user is authorised to view a student's records.

    Args:
        user: The currently authenticated user.
        student_id: Primary key of the student whose records are being requested.

    Returns:
        True if the user is the student, an admin, or a doctor who has seen
        the student; False otherwise.
    """
    role = user.role_name.lower()
    if role == "admin":
        return True
    if role in PATIENT_ROLES:
        return student_id == get_student_id_for_user(user.user_id)
    if role == "doctor":
        staff_id = get_staff_id_for_user(user.user_id)
        return doctor_repo.has_doctor_seen_student(staff_id, student_id)
    return False
