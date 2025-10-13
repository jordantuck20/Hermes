# utils/db_config.py
import logging
import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL, create_engine

logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv()

# --- Database Configuration ---
DB_USER = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT", "3306")
DB_NAME = os.getenv("DATABASE_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    logger.error(
        "Missing one or more database environment variables (DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME)."
    )
    logger.error("Please set them up in your .env file or hosting environment.")
    raise ValueError(
        "Database connection environment variables are not fully configured. Please check your .env file."
    )

DATABASE_URL = URL.create(
    drivername="mysql+mysqlconnector",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

ENGINE = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
