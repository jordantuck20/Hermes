# utils/bot_database.py
import logging
from contextlib import contextmanager

from db_config import ENGINE
from models import Base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


# --- Session Management ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


@contextmanager
def get_db_session():
    """Yields a database session. Use with 'with' statement for automatic closing."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_tables():
    """Creates all defined tables in the database."""
    logger.info("Attempting to create database tables...")
    Base.metadata.create_all(ENGINE)
    logger.info("Database tables created or already exist.")
