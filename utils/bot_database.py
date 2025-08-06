# utils/bot_database.py
import logging
import os
from contextlib import contextmanager
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

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
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

Base = declarative_base()


# --- Model definitions ---
class Game(Base):
    """Represents a game from Steam."""

    __tablename__ = "games"

    steam_id = Column(BigInteger, primary_key=True, comment="Steam Application ID")
    game_name = Column(String(255), nullable=False, comment="Human-readable game name")
    last_checked = Column(
        DateTime, nullable=True, comment="Timestamp of last news check from Steam API"
    )

    subscriptions = relationship(
        "Subscription", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Game(steam_id={self.steam_id}, game_name='{self.game_name}')>"


class DiscordServer(Base):
    """Represents a Discord server (guild) configuration."""

    __tablename__ = "discord_servers"

    server_id = Column(BigInteger, primary_key=True, comment="Discord Guild ID")
    channel_id = Column(
        BigInteger, nullable=False, comment="Discord Channel ID for news updates"
    )
    server_name = Column(
        String(255),
        nullable=True,
        comment="Name of the Discord server (for logging/admin)",
    )
    prefix = Column(
        String(10),
        nullable=True,
        default="!",
        comment="Bot command prefix for this server",
    )
    timezone = Column(
        String(50), nullable=True, comment="Timezone for specific scheduling needs"
    )

    subscriptions = relationship(
        "Subscription", back_populates="server", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<DiscordServer(server_id={self.server_id}, channel_id={self.channel_id})>"
        )


class Subscription(Base):
    """Represents a subscription of a Discord server to a specific game."""

    __tablename__ = "subscriptions"

    subscription_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique ID for this subscription",
    )
    server_id = Column(
        BigInteger,
        ForeignKey("discord_servers.server_id"),
        nullable=False,
        comment="Discord Guild ID",
    )
    steam_id = Column(
        BigInteger,
        ForeignKey("games.steam_id"),
        nullable=False,
        comment="Steam Application ID",
    )
    last_news_item_timestamp = Column(
        BigInteger,
        nullable=True,
        comment="GID of the last news item sent for this subscription",
    )
    channel_id_override = Column(
        BigInteger,
        nullable=True,
        comment="Specific channel ID if different from server's default",
    )

    __table_args__ = (
        UniqueConstraint("server_id", "steam_id", name="_server_steam_uc"),
    )

    server = relationship("DiscordServer", back_populates="subscriptions")
    game = relationship("Game", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(server_id={self.server_id}, steam_id={self.steam_id}, last_news_item_timestamp={self.last_news_item_timestamp})>"


# --- Session Management ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    Base.metadata.create_all(engine)
    logger.info("Database tables created or already exist.")
