# utils/steam_api.py
import logging

import requests

logger = logging.getLogger(__name__)

STEAM_NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"


def fetch_steam_news(appid: int, count: int = 1, maxlength: int = 300) -> list[dict]:
    """
    Fetches the latest news items for a given app ID from the Steam API.

    This function sends an HTTP GET request to the public Steam News API and
    retrieves a list of news items for a specified game. It handles network
    errors and unexpected API responses gracefully.

    Args:
        appid (int): The Steam Application ID for the game.
        count (int, optional): The number of news items to fetch. Defaults to 1.
        maxlength (int, optional): The maximum length of the news item content. Defaults to 300.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a news item. Returns an empty list on error or if no news is found.
    """
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
