# utils/steam_api.py
import logging

import requests

logger = logging.getLogger(__name__)

STEAM_NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"


def fetch_steam_news(appid: int, count: int = 1, maxlength: int = 300) -> list[dict]:
    params = {"appid": appid, "count": count, "maxlength": maxlength}
    try:
        response = requests.get(STEAM_NEWS_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        newsitems = data.get("appnews", {}).get("newsitems", [])
        return newsitems
    except Exception as e:
        logger.error(f"Error fetching Steam news for appid {appid}: {e}")
        return []
