from fastapi import HTTPException


class ServiceError(Exception):
    status_code = 400


class NotFoundError(ServiceError):
    status_code = 404


class UnauthorizedError(ServiceError):
    status_code = 401


class ConflictError(ServiceError):
    status_code = 409


class DatabaseNotConfiguredError(ServiceError):
    status_code = 503


def service_error_to_http(exc: Exception) -> HTTPException:
    if isinstance(exc, ServiceError):
        return HTTPException(status_code=exc.status_code, detail=str(exc))
    if isinstance(exc, RuntimeError):
        return HTTPException(status_code=503, detail="Service temporarily unavailable")
    return HTTPException(status_code=500, detail="Internal server error")
