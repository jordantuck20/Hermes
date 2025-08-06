# utils/game_manager.py
import logging
from typing import Dict, Optional

from utils.bot_database import Game, get_db_session

logger = logging.getLogger(__name__)


class GameManager:
    def __init__(self):
        """
        Initializes the GameManager and loads game data from the database.

        The GameManager is responsible for providing fast, in-memory lookups
        of game information, such as converting a Steam App ID to a game name
        and vice versa. The game data is loaded from the database into
        two dictionaries upon intialization.

        Attributes:
            appid_to_name (Dict[int, str]): A dictionary that maps a Steam App ID to its game name.
            name_to_appid (Dict[str, int]): A dictionary that maps a game name to its Steam App ID.
        """
        self.appid_to_name: Dict[int, str] = {}
        self.name_to_appid: Dict[str, int] = {}

        self.load_games_from_db()

    def load_games_from_db(self) -> None:
        """
        Loads all game datga from the database into the GameManager's in-memory cache.

        This method clears the existing in-memory dictionaries and repopulates them
        by querying the `game` table in the database. This ensures the bot's cache
        is up-to-date with the latest game information.
        """
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
        """
        Gets a human-readable name of a game by its Steam App ID.

        This method performs a fast lookup in the in-memory cache to retrieve the
        name of a game. If the App ID is not found, it returns a default string.

        Args:
            appid (int): The Steam Application ID of the game.

        Returns:
            str: The game's name or the string "Unknown Game" if the ID is not found.
        """
        return self.appid_to_name.get(appid, "Unknown Game")

    def get_appid_by_name(self, game_name: str) -> Optional[int]:
        """
        Gets the Steam App ID of a game by its name.

        This method performs a fast, case-insensitive lookup in the in-memory cache
        to retrieve the Steam App ID for a given game name.

        Args:
            game_name (str): The human-readable name of the game.

        Returns:
            Optional[int]: The game's Steam App ID, or None if the name is not found.
        """
        return self.name_to_appid.get(game_name.lower())

    def add_game(self, steam_id: int, game_name: str) -> None:
        """
        Adds a new game to the database or updates an existing one.

        This method first checks if a game with the given Steam App ID already exists.
        If it's a new game, it is added to the database. If it's an existing game,
        its name is updated if it has changed. The in-memory cache is then updated
        to reflect the change.

        Args:
            steam_id (int): The Steam Application ID for the game.
            game_name (str): The human-readable name of the game.
        """
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
                    self.appid_to_name[steam_id] = game_name
                    self.name_to_appid[game_name.lower()] = steam_id

            except Exception as e:
                session.rollback()
                logger.error(
                    f"Failed to add or update game {game_name} (ID: {steam_id}): {e}",
                    exc_info=True,
                )
