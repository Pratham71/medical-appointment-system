from fastapi.testclient import TestClient

from app.backend.app.api.errors import service_error_to_http
from app.backend.app.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_logout_endpoint_returns_success_message():
    client = TestClient(app)

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}


def test_unexpected_errors_do_not_expose_internal_details():
    error = service_error_to_http(RuntimeError("database password leaked"))

    assert error.status_code == 503
    assert error.detail == "Service temporarily unavailable"


def test_openapi_includes_mvp_routes():
    client = TestClient(app)

    paths = client.get("/openapi.json").json()["paths"]

    expected_paths = {
        "/auth/login",
        "/auth/logout",
        "/auth/me",
        "/students/dashboard",
        "/students/appointments",
        "/students/reports",
        "/students/certificates",
        "/doctors/dashboard",
        "/doctors/appointments",
        "/doctors/appointment/{appointment_id}",
        "/doctors/patient-history/{student_id}",
        "/appointments/slots",
        "/appointments/book",
        "/appointments/{appointment_id}/cancel",
        "/appointments/{appointment_id}/complete",
        "/reports/{appointment_id}/notes",
        "/reports/{appointment_id}/prescription",
        "/reports/{appointment_id}",
        "/certificates/{appointment_id}",
        "/certificates/student/{student_id}",
    }

    assert expected_paths.issubset(paths.keys())
