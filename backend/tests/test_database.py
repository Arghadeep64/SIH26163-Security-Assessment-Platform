"""Tests for database configuration loading and ORM models."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.config import Settings, PROJECT_ROOT, ENV_FILE_PATH
from app.database import check_db_connection
from app.models import Assessment, SecurityCheck, Finding, Evidence, Report


def test_settings_root_env_path_resolution():
    """Verify that PROJECT_ROOT and ENV_FILE_PATH are derived from config.py location."""
    assert PROJECT_ROOT.exists()
    assert (PROJECT_ROOT / "backend").exists()
    assert ENV_FILE_PATH == PROJECT_ROOT / ".env"
    assert ENV_FILE_PATH.name == ".env"


def test_settings_loaded_regardless_of_cwd(tmp_path):
    """Verify Settings loads from project-root .env even when CWD is changed to backend or subdirs."""
    original_cwd = os.getcwd()
    try:
        # Change working directory to backend or a temp directory
        backend_dir = PROJECT_ROOT / "backend"
        os.chdir(str(backend_dir))

        # Instantiating Settings should resolve root .env via absolute ENV_FILE_PATH
        settings = Settings()
        assert settings.model_config["env_file"] == ENV_FILE_PATH
        assert settings.DB_NAME is not None
    finally:
        os.chdir(original_cwd)


def test_settings_default_values():
    """Verify default database settings."""
    settings = Settings()
    assert settings.DB_HOST in ["127.0.0.1", "localhost"] or len(settings.DB_HOST) > 0
    assert settings.DB_PORT in [3306, 4000] or settings.DB_PORT > 0
    assert settings.DB_NAME == "sih26163_db"
    assert "mysql+pymysql://" in settings.database_url


def test_settings_environment_override():
    """Verify settings load overrides from environment variables properly."""
    custom_env = {
        "DB_HOST": "tidb-cluster.region.prod.tidbcloud.com",
        "DB_PORT": "4000",
        "DB_NAME": "sih26163_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "secret_password_123",
    }
    with patch.dict(os.environ, custom_env, clear=False):
        settings = Settings()
        assert settings.DB_HOST == "tidb-cluster.region.prod.tidbcloud.com"
        assert settings.DB_PORT == 4000
        assert settings.DB_NAME == "sih26163_db"
        assert settings.DB_USER == "test_user"
        assert settings.DB_PASSWORD == "secret_password_123"
        assert "mysql+pymysql://test_user:secret_password_123@tidb-cluster.region.prod.tidbcloud.com:4000/sih26163_db" == settings.database_url


def test_settings_password_masking():
    """Verify DB_PASSWORD is not exposed in logs or string representations."""
    settings = Settings(DB_PASSWORD="super_secret_password")
    repr_str = repr(settings)
    assert "super_secret_password" not in repr_str
    assert "******" in repr_str

    safe_dict = settings.get_safe_settings_dict()
    assert safe_dict["DB_PASSWORD"] == "******"
    assert "super_secret_password" not in str(safe_dict)


def test_check_db_connection_exception_handling():
    """Verify check_db_connection handles connection exceptions gracefully."""
    with patch("app.database.engine.connect", side_effect=Exception("Database connection timeout")):
        result = check_db_connection()
        assert result is False


def test_check_db_connection_success():
    """Verify check_db_connection returns True on successful ping."""
    mock_conn = MagicMock()
    with patch("app.database.engine.connect") as mock_connect:
        mock_connect.return_value.__enter__.return_value = mock_conn
        result = check_db_connection()
        assert result is True
        mock_conn.execute.assert_called_once()


def test_orm_models_table_names():
    """Verify SQLAlchemy ORM models define the expected tables."""
    assert Assessment.__tablename__ == "assessments"
    assert SecurityCheck.__tablename__ == "security_checks"
    assert Finding.__tablename__ == "findings"
    assert Evidence.__tablename__ == "evidence"
    assert Report.__tablename__ == "reports"


def test_orm_models_key_columns():
    """Verify essential columns exist on ORM models."""
    assert "target_url" in Assessment.__table__.columns
    assert "status" in Assessment.__table__.columns
    assert "check_id" in SecurityCheck.__table__.columns
    assert "finding_code" in Finding.__table__.columns
    assert "severity" in Finding.__table__.columns
    assert "evidence_type" in Evidence.__table__.columns
    assert "redacted" in Evidence.__table__.columns
    assert "report_type" in Report.__table__.columns
