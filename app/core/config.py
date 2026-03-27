from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="WEIS", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    default_language: str = Field(default="en", alias="DEFAULT_LANGUAGE")
    supported_languages: str = Field(default="en,fr", alias="SUPPORTED_LANGUAGES")
    default_currency: str = Field(default="XAF", alias="DEFAULT_CURRENCY")
    database_url: str = Field(default="sqlite:///./weis.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    s3_endpoint_url: str = Field(default="", alias="S3_ENDPOINT_URL")
    s3_bucket: str = Field(default="weis-documents", alias="S3_BUCKET")
    s3_access_key: str = Field(default="", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="", alias="S3_SECRET_KEY")
    sms_provider: str = Field(default="stub", alias="SMS_PROVIDER")
    sms_sender_id: str = Field(default="WEIS", alias="SMS_SENDER_ID")
    payment_provider: str = Field(default="stub", alias="PAYMENT_PROVIDER")
    mobile_money_provider: str = Field(default="stub", alias="MOBILE_MONEY_PROVIDER")
    maps_provider: str = Field(default="stub", alias="MAPS_PROVIDER")
    sentry_dsn: str = Field(default="", alias="SENTRY_DSN")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
