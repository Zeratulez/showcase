import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str

    REDIS_URL: str = "redis://localhost:6379"
    REDIS_RATE_LIMIT_REQUESTS: int = 10
    REDIS_RATE_LIMIT_WINDOW: int = 60

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

settings = Settings()