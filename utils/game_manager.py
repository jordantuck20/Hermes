# utils/game_manager.py
import logging
from typing import Optional, Dict

from utils.bot_database import get_db_session, Game

logger = logging.getLogger(__name__)


class GameManager:
    def __init__(self):
        self.appid_to_name: Dict[int, str] = {}
        self.name_to_appid: Dict[str, int] = {}

        self.load_games_from_db()

    def load_games_from_db(self) -> None:
        """Loads all game data from the database into in-memory dictionary"""
        self.appid_to_name.clear()
        self.name_to_appid.clear()

        with get_db_session() as session:
            try:
                games = session.query(Game).all()
                for game in games:
                    self.appid_to_name[game.steam_id] = game.game_name
                    self.name_to_appid[game.game_name.lower()] = game.steam_id
                logger.info(f"Loaded {len(games)} games from the database.")
            except Exception as e:
                logger.error(f"Failed to load games from database: {e}", exc_info=True)

    def get_name(self, appid: int) -> str:
        """Gets the human-readable name of a game by its Steam App ID"""
        return self.appid_to_name.get(appid, "Unknown Game")

    def get_appid_by_name(self, game_name: str) -> Optional[int]:
        """Gets the Steam App ID of a game by its name (case-insensitive)"""
        return self.name_to_appid.get(game_name.lower())

    def add_game(self, steam_id: int, game_name: str) -> None:
        """Adds a new game to the database and updates in-memory cache."""
        with get_db_session() as session:
            try:
                # Check if game already exists
                existing_game = session.query(Game).filter_by(steam_id=steam_id).first()
                needs_commit = False

                if existing_game:
                    # Update name if different, or just log
                    if existing_game.game_name != game_name:
                        existing_game.game_name = game_name
                        logger.info(f"Updated game name for {steam_id} to {game_name}")
                        needs_commit = True
                    else:
                        logger.info(
                            f"Game {game_name} (ID: {steam_id}) already exists."
                        )
                else:
                    new_game = Game(steam_id=steam_id, game_name=game_name)
                    session.add(new_game)
                    logger.info(
                        f"Added new game to database: {game_name} (ID: {steam_id})"
                    )
                    needs_commit = True

                if needs_commit:
                    session.commit()
                    self._load_games_from_db()

            except Exception as e:
                session.rollback()
                logger.error(
                    f"Failed to add or update game {game_name} (ID: {steam_id}): {e}",
                    exc_info=True,
                )
