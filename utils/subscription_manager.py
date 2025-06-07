from utils.config_manager import ConfigManager
from typing import Any


class SubscriptionManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def get_subscriptions(self, guild_id: int) -> list[int]:
        guild_cfg: dict[str, Any] = self.config_manager.get_guild_config(guild_id)
        return guild_cfg.get("subscriptions", [])

    def add_subscription(self, guild_id: int, appid: int) -> None:
        guild_cfg: dict[str, Any] = self.config_manager.get_guild_config(guild_id)
        subs: set[int] = set(guild_cfg.get("subscriptions", []))
        subs.add(appid)
        guild_cfg["subscriptions"] = list(subs)
        self.config_manager.update_guild_config(guild_id, guild_cfg)

    def remove_subscription(self, guild_id: int, appid: int) -> None:
        guild_cfg: dict[str, Any] = self.config_manager.get_guild_config(guild_id)
        subs: set[int] = set(guild_cfg.get("subscriptions", []))
        subs.discard(appid)
        guild_cfg["subscriptions"] = list(subs)
        self.config_manager.update_guild_config(guild_id, guild_cfg)
