# utils/news_manager.py
from utils.steam_api import fetch_steam_news
from utils.config_manager import ConfigManager
from typing import Any


class NewsManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def get_last_news_id(self, guild_id: int, appid: int) -> str | None:
        guild_cfg: dict[str, Any] = self.config_manager.get_guild_config(guild_id)
        last_news: dict[str, str] = guild_cfg.get("last_news", {})
        return last_news.get(str(appid))

    def save_last_news_id(self, guild_id: int, appid: int, news_gid: str) -> None:
        guild_cfg: dict[str, Any] = self.config_manager.get_guild_config(guild_id)
        last_news: dict[str, str] = guild_cfg.get("last_news", {})
        last_news[str(appid)] = news_gid
        guild_cfg["last_news"] = last_news
        self.config_manager.update_guild_config(guild_id, guild_cfg)

    def fetch_latest_news(self, appid: int, count: int = 1) -> list[dict[str, Any]]:
        return fetch_steam_news(appid, count=count)
