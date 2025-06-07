import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self, config_file: str = "data/server_configs.json"):
        self.config_file = config_file
        self.configs: dict[str, Any] = self.load_configs()

    def load_configs(self) -> dict[str, Any]:
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load configs from {self.config_file}: {e}")
            raise

    def save_configs(self) -> None:
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.configs, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save configs to {self.config_file}: {e}")
            raise

    def get_guild_config(self, guild_id: int) -> dict[str, Any]:
        return self.configs.get(str(guild_id), {})

    def update_guild_config(self, guild_id: int, guild_config: dict[str, Any]) -> None:
        self.configs[str(guild_id)] = guild_config
        self.save_configs()
