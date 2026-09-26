"""Application configuration module."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Derive the project root directory from this file's location (backend/app/config.py -> SIH26163)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and root .env file."""

    # Application settings
    APP_ENV: str = Field(default="development", description="Application environment")
    BACKEND_HOST: str = Field(default="127.0.0.1", description="Backend host")
    BACKEND_PORT: int = Field(default=8000, description="Backend port")
    DEFAULT_TARGET: str = Field(
        default="http://localhost:3000",
        description="Default assessment target URL",
    )

    # Database settings (MySQL / TiDB)
    DB_HOST: str = Field(default="127.0.0.1", description="Database host")
    DB_PORT: int = Field(default=3306, description="Database port")
    DB_NAME: str = Field(default="sih26163_db", description="Database name")
    DB_USER: str = Field(default="root", description="Database user")
    DB_PASSWORD: str = Field(default="", description="Database password")

    @property
    def database_url(self) -> str:
        """Construct the MySQL/TiDB compatible SQLAlchemy connection URL using PyMySQL."""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_safe_settings_dict(self) -> dict[str, object]:
        """Return a dictionary of settings with sensitive fields redacted for safe logging."""
        return {
            "APP_ENV": self.APP_ENV,
            "BACKEND_HOST": self.BACKEND_HOST,
            "BACKEND_PORT": self.BACKEND_PORT,
            "DEFAULT_TARGET": self.DEFAULT_TARGET,
            "DB_HOST": self.DB_HOST,
            "DB_PORT": self.DB_PORT,
            "DB_NAME": self.DB_NAME,
            "DB_USER": self.DB_USER,
            "DB_PASSWORD": "******" if self.DB_PASSWORD else "",
        }

    def __repr__(self) -> str:
        safe_repr = ", ".join(f"{k}={v!r}" for k, v in self.get_safe_settings_dict().items())
        return f"Settings({safe_repr})"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
