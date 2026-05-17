from fastapi import APIRouter

from app.backend.app.api.routes import (
    admin,
    appointments,
    auth,
    certificates,
    doctors,
    emergencies,
    reports,
    students,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(emergencies.router)
api_router.include_router(reports.router)
api_router.include_router(certificates.router)
api_router.include_router(admin.router)
