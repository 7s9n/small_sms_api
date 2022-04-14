from functools import lru_cache
from typing import (
    Any,
    Dict,
    Optional,
)
from pydantic import (
    BaseSettings,
    PostgresDsn,
    validator
)


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI School Management System"
    API_V1_STR: str = "/api/v1"
    
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            path=f"/{values.get('DB_NAME') or  ''}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
