from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CampusGuard 校园吸烟检测系统"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:666666@localhost:5432/campus_guard"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_prefix = "CG_"


settings = Settings()
