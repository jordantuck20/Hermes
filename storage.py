import json
import os

CONFIG_FILE = "data/server_configs.json"


def load_configs():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_configs(configs):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(configs, f, indent=4)


def set_update_channel(guild_id: int, channel_id: int):
    configs = load_configs()
    configs[str(guild_id)] = {"update_channel_id": channel_id}
    save_configs(configs)


def get_update_channel(guild_id: int):
    configs = load_configs()
    guild_config = configs.get(str(guild_id))
    if guild_config:
        return guild_config.get("update_channel_id")
    return None


def save_last_news_id(guild_id: int, appid: int, news_gid: str):
    configs = load_configs()
    guild_cfg = configs.get(str(guild_id), {})
    if "last_news" not in guild_cfg:
        guild_cfg["last_news"] = {}
    guild_cfg["last_news"][str(appid)] = news_gid
    configs[str(guild_id)] = guild_cfg
    save_configs(configs)


def get_last_news_id(guild_id: int, appid: int):
    configs = load_configs()
    guild_cfg = configs.get(str(guild_id), {})
    last_news = guild_cfg.get("last_news", {})
    return last_news.get(str(appid))
