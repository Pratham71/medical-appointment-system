from datetime import date
from typing import Any

from app.backend.app.db import session
from app.backend.app.db.queries import admin_queries


_PATIENT_ROLES = {"student", "professor", "college-staff", "hostel-staff"}


def get_dashboard_counts() -> dict[str, Any] | None:
    with session.connection_scope() as connection:
        return admin_queries.get_dashboard_counts(connection)


def list_users(
    search_text: str | None,
    role_name: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_users(
            connection,
            search_text=search_text,
            role_name=role_name,
            limit=limit,
        )


def assign_user_role(
    *,
    user_id: int,
    role_name: str,
    roll_number: str | None,
    department: str | None,
    year_level: int | None,
    employee_number: str | None,
    specialization: str | None,
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        context = admin_queries.get_user_role_context(connection, user_id)
        if context is None:
            return None

        role = admin_queries.get_role_id(connection, role_name)
        if role is None:
            return None

        student_appointments = int(context["student_appointment_count"] or 0)
        staff_slots = int(context["staff_slot_count"] or 0)
        if role_name not in _PATIENT_ROLES and student_appointments > 0:
            return {
                "conflict": True,
                "message": "Cannot remove patient profile with appointment history",
            }
        if role_name not in {"doctor", "staff"} and staff_slots > 0:
            return {
                "conflict": True,
                "message": "Cannot remove staff profile with appointment slots",
            }

        admin_queries.update_user_role(
            connection,
            user_id=user_id,
            role_id=int(role["role_id"]),
        )

        if role_name in _PATIENT_ROLES:
            _save_patient_profile(
                connection,
                user_id=user_id,
                roll_number=roll_number or "",
                department=department or "",
                year_level=year_level or 1,
            )
            if context["staff_id"] is not None:
                admin_queries.delete_staff_profile(connection, user_id)
        elif role_name in {"doctor", "staff"}:
            _save_staff_profile(
                connection,
                user_id=user_id,
                employee_number=employee_number or "",
                specialization=specialization,
                is_doctor=role_name == "doctor",
            )
            if context["student_id"] is not None:
                admin_queries.delete_student_profile(connection, user_id)
        elif role_name == "admin":
            if context["student_id"] is not None:
                admin_queries.delete_student_profile(connection, user_id)
            if context["staff_id"] is not None:
                admin_queries.delete_staff_profile(connection, user_id)

        return admin_queries.get_role_assignment_result(connection, user_id)


def set_user_active_status(
    *,
    user_id: int,
    is_active: bool,
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        context = admin_queries.get_user_status_context(connection, user_id)
        if context is None:
            return None
        admin_queries.update_user_active_status(
            connection,
            user_id=user_id,
            is_active=is_active,
        )
        return {
            "user_id": user_id,
            "is_active": is_active,
        }


def list_appointments(
    *,
    status: str | None,
    from_date: date | None,
    to_date: date | None,
    doctor_id: int | None,
    student_id: int | None,
    limit: int,
) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_appointments(
            connection,
            status=status,
            from_date=from_date,
            to_date=to_date,
            doctor_id=doctor_id,
            student_id=student_id,
            limit=limit,
        )


def list_students(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_students(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_doctors(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_doctors(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_staff(search_text: str | None, limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_staff(
            connection,
            search_text=search_text,
            limit=limit,
        )


def list_emergency_alerts(limit: int) -> list[dict[str, Any]]:
    with session.connection_scope() as connection:
        return admin_queries.list_emergency_alerts(connection, limit=limit)


def acknowledge_emergency_alert(
    *,
    alert_id: int,
    actor_user_id: int,
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        context = admin_queries.get_emergency_alert_for_update(connection, alert_id)
        if context is None:
            return None
        admin_queries.acknowledge_emergency_alert(
            connection,
            alert_id=alert_id,
            actor_user_id=actor_user_id,
        )
        return admin_queries.get_emergency_alert_summary(connection, alert_id)


def resolve_emergency_alert(
    *,
    alert_id: int,
    actor_user_id: int,
    resolution_note: str | None,
) -> dict[str, Any] | None:
    with session.transaction_scope() as connection:
        context = admin_queries.get_emergency_alert_for_update(connection, alert_id)
        if context is None:
            return None
        admin_queries.resolve_emergency_alert(
            connection,
            alert_id=alert_id,
            actor_user_id=actor_user_id,
            resolution_note=resolution_note,
        )
        return admin_queries.get_emergency_alert_summary(connection, alert_id)


def _save_patient_profile(
    connection: Any,
    *,
    user_id: int,
    roll_number: str,
    department: str,
    year_level: int,
) -> None:
    profile = admin_queries.get_student_profile_by_user_id(connection, user_id)
    if profile is None:
        admin_queries.insert_student_profile(
            connection,
            user_id=user_id,
            roll_number=roll_number,
            department=department,
            year_level=year_level,
        )
    else:
        admin_queries.upsert_student_profile(
            connection,
            user_id=user_id,
            roll_number=roll_number,
            department=department,
            year_level=year_level,
        )


def _save_staff_profile(
    connection: Any,
    *,
    user_id: int,
    employee_number: str,
    specialization: str | None,
    is_doctor: bool,
) -> None:
    profile = admin_queries.get_staff_profile_by_user_id(connection, user_id)
    if profile is None:
        admin_queries.insert_staff_profile(
            connection,
            user_id=user_id,
            employee_number=employee_number,
            specialization=specialization,
            is_doctor=is_doctor,
        )
    else:
        admin_queries.upsert_staff_profile(
            connection,
            user_id=user_id,
            employee_number=employee_number,
            specialization=specialization,
            is_doctor=is_doctor,
        )
