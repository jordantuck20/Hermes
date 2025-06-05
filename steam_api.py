import requests

STEAM_NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"


def fetch_steam_news(appid, count=1, maxlength=300):
    params = {"appid": appid, "count": count, "maxlength": maxlength}
    try:
        response = requests.get(STEAM_NEWS_URL, params=params)
        response.raise_for_status()
        data = response.json()
        newsitems = data.get("appnews", {}).get("newsitems", [])
        return newsitems
    except Exception as e:
        print(f"Error fetching Steam news: {e}")
        return []
