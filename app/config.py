from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/payment_db"
    SECRET_KEY: str = "gfdmhghif38yrf9ew0jkf32"
    JWT_SECRET: str = "change-me-to-a-strong-random-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600


settings = Settings()
