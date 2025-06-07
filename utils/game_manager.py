import json
import logging

logger = logging.getLogger(__name__)


class GameManager:
    def __init__(self, games_file="data/games.json"):
        self.appid_to_name = {}
        try:
            with open(games_file, "r") as f:
                self.games = json.load(f)
            self.appid_to_name = {
                int(appid): name for name, appid in self.games.items()
            }
        except Exception as e:
            logger.error(f"Failed to load games from {games_file}: {e}")

    def get_name(self, appid: int) -> str:
        return self.appid_to_name.get(appid, "Unknown game")
