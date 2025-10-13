# utils/bot_database.py
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    TinyInteger,
    create_engine,
    func,
)
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

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


class Base(DeclarativeBase):
    pass


# --- Model definitions ---
class Guild(Base):
    """Represents a Discord guild (server)."""

    __tablename__ = "guilds"

    # Columns
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_name: Mapped[str] = mapped_column(String(255))
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="guild", cascade="all, delete-orphan"
    )
    delivery_logs: Mapped[List["DeliveryLog"]] = relationship(
        back_populates="guild", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Guild(id={self.guild_id}, guild_name='{self.guild_name}', channel_id={self.channel_id})>"


class Game(Base):
    """Represents a game from Steam."""

    __tablename__ = "games"

    # Columns
    app_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, comment="Steam Application ID"
    )
    game_name: Mapped[str] = mapped_column(
        String(255), comment="Human-readable game name"
    )
    date_added: Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.now(),
        comment="Timestamp of when game was added to the database",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Flag indicating if the game is actively tracked"
    )

    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )
    news_items: Mapped[List["NewsItem"]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Game(app_id={self.app_id}, game_name='{self.game_name}')>"


class Subscription(Base):
    """Represents a link table: which guild is subscribed to which game."""

    __tablename__ = "subscriptions"

    # Columns
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("guilds.guild_id"), primary_key=True, type_=BigInteger
    )
    app_id: Mapped[int] = mapped_column(
        ForeignKey("games.app_id"), primary_key=True, type_=BigInteger
    )
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=True)
    subscribed_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    # Relationships
    guild: Mapped[Guild] = relationship(back_populates="subscriptions")
    game: Mapped[Game] = relationship(back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(guild_id={self.guild_id}, app_id={self.app_id}, is_subscribed={self.is_subscribed})>"


class NewsItem(Base):
    """Represents a specific news article for a game."""

    __tablename__ = "news_items"

    # Columns
    news_gid: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    app_id: Mapped[int] = mapped_column(ForeignKey("games.app_id"), type_=BigInteger)
    title: Mapped[str] = mapped_column(String(255))
    date_fetched: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    # Relationships
    game: Mapped[Game] = relationship(back_populates="news_items")
    delivery_logs: Mapped[List["DeliveryLog"]] = relationship(
        back_populates="news_item", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<NewsItem(gid={self.news_gid}, app_id={self.app_id}, title='{self.title[:20]}...')>"


class DeliveryLog(Base):
    """Represents the status of delivering a news item to a guild."""

    __tablename__ = "delivery_log"

    # Columns
    news_gid: Mapped[int] = mapped_column(
        ForeignKey("news_items.news_gid"), primary_key=True, type_=BigInteger
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("guilds.guild_id"), primary_key=True, type_=BigInteger
    )
    delivery_status: Mapped[str] = mapped_column(String(50))
    delivered_at: Mapped[DateTime] = mapped_column(DateTime)
    attempt_count: Mapped[int] = mapped_column(TinyInteger, default=1)
    error_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    news_item: Mapped[NewsItem] = relationship(back_populates="delivery_logs")
    guild: Mapped[Guild] = relationship(back_populates="delivery_logs")

    def __repr__(self):
        return f"<DeliveryLog(news_gid={self.news_gid}, guild_id={self.guild_id}, status='{self.delivery_status}')>"


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
