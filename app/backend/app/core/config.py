from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "College Infirmary Appointment API"
    app_version: str = "beta-1.1.0"
    environment: str = "development"
    jwt_secret_key: str = "change-this-dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_provider: str = "mysql"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "medical_appointment_system"
    mysql_pool_name: str = "medical_appointment_pool"
    mysql_pool_size: int = 5
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 120
    login_max_failed_attempts: int = 5
    login_lockout_seconds: int = 300
    idempotency_key_ttl_seconds: int = 600
    email_notifications_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Enforce strong JWT secret when the environment is set to production.

        Returns:
            The validated Settings instance.

        Raises:
            ValueError: If the JWT secret key is the default placeholder or
                shorter than 32 characters in production.
        """
        if self.environment.lower() == "production":
            if (
                self.jwt_secret_key == "change-this-dev-secret"
                or len(self.jwt_secret_key) < 32
            ):
                raise ValueError("JWT_SECRET_KEY must be strong in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Returns:
        The global Settings instance, loaded once from environment variables
        and cached for the lifetime of the process.
    """
    return Settings()
