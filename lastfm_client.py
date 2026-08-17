import os

import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API = os.environ["LASTFM_API"]

BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def get_top_tags(artist: str, track: str) -> list:
    """Community tags for a track, using canonical artist/track strings. Empty list if not found."""
    response = requests.get(
        BASE_URL,
        params={
            "method": "track.getTopTags",
            "artist": artist,
            "track": track,
            "api_key": LASTFM_API,
            "format": "json",
        },
    )
    response.raise_for_status()
    payload = response.json()

    if "error" in payload:
        return []

    tags = payload.get("toptags", {}).get("tag", [])
    return [tag["name"] for tag in tags]


if __name__ == "__main__":
    import sys

    artist = sys.argv[1] if len(sys.argv) > 1 else "Dua Lipa"
    track = sys.argv[2] if len(sys.argv) > 2 else "Levitating"
    print(get_top_tags(artist, track))
