from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "College Infirmary Appointment API"
    app_version: str = "0.1.0"
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
