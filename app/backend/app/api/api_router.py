from fastapi import APIRouter

from app.backend.app.api.routes import (
    appointments,
    auth,
    certificates,
    doctors,
    reports,
    students,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(reports.router)
api_router.include_router(certificates.router)
