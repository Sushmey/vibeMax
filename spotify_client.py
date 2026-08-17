import base64
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT = os.environ["SPOTIFY_CLIENT"]
SPOTIFY_SECRET = os.environ["SPOTIFY_SECRET"]

TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"
TRACK_URL = "https://api.spotify.com/v1/tracks/{track_id}"

_token_cache = {"access_token": None, "expires_at": 0}


def get_access_token() -> str:
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT}:{SPOTIFY_SECRET}".encode()).decode()
    response = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {auth_header}"},
        data={"grant_type": "client_credentials"},
    )
    response.raise_for_status()
    payload = response.json()

    _token_cache["access_token"] = payload["access_token"]
    _token_cache["expires_at"] = time.time() + payload["expires_in"] - 60
    return _token_cache["access_token"]


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_access_token()}"}


def search_track(query: str) -> dict | None:
    """Resolve free-text user input to a Spotify track. Returns None if no match."""
    response = requests.get(
        SEARCH_URL,
        headers=_auth_headers(),
        params={"q": query, "type": "track", "limit": 1},
    )
    response.raise_for_status()
    items = response.json()["tracks"]["items"]
    return items[0] if items else None


def get_track(spotify_id: str) -> dict:
    """Full track metadata for a known Spotify ID (cold-start build step)."""
    response = requests.get(TRACK_URL.format(track_id=spotify_id), headers=_auth_headers())
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "levitating dua lipa"
    print("token ok:", bool(get_access_token()))
    track = search_track(query)
    print(track)
