"""Database connection preparation module for SQLAlchemy and PyMySQL.

Schema and tables are managed via SQL scripts:
- database/mysql/sih26163_schema.sql (local MySQL)
- database/tidb/sih26163_schema.sql (TiDB cloud/production)
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# MySQL / TiDB compatible engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency provider for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Safely test whether the configured database connection is reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
