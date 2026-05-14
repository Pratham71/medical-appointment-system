from fastapi import FastAPI

from app.backend.app.api.api_router import api_router
from app.backend.app.core.config import get_settings
from app.backend.app.core.security_controls import security_request_middleware

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.middleware("http")(security_request_middleware)
app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
