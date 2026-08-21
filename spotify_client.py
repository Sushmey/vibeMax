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
TRACKS_URL = "https://api.spotify.com/v1/tracks"

_token_cache = {"access_token": None, "expires_at": 0}


def _request_with_retry(method: str, url: str, max_retries: int = 3, **kwargs) -> requests.Response:
    """requests call that waits out Spotify's 429 Retry-After instead of failing immediately."""
    for attempt in range(max_retries):
        response = requests.request(method, url, **kwargs)
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 5))
            print(f"Spotify rate limited, waiting {wait}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(wait)
            continue
        if not response.ok:
            print("Spotify error response:", response.text, flush=True)
        response.raise_for_status()
        return response

    response.raise_for_status()
    return response


def get_access_token() -> str:
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT}:{SPOTIFY_SECRET}".encode()).decode()
    response = _request_with_retry(
        "post",
        TOKEN_URL,
        headers={"Authorization": f"Basic {auth_header}"},
        data={"grant_type": "client_credentials"},
    )
    payload = response.json()

    _token_cache["access_token"] = payload["access_token"]
    _token_cache["expires_at"] = time.time() + payload["expires_in"] - 60
    return _token_cache["access_token"]


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_access_token()}"}


def search_track(query: str) -> dict | None:
    """Resolve free-text user input to a Spotify track. Returns None if no match."""
    response = _request_with_retry(
        "get",
        SEARCH_URL,
        headers=_auth_headers(),
        params={"q": query, "type": "track", "limit": 1},
    )
    items = response.json()["tracks"]["items"]
    return items[0] if items else None


def get_track(spotify_id: str) -> dict:
    """Full track metadata for a known Spotify ID (cold-start build step)."""
    response = _request_with_retry("get", TRACK_URL.format(track_id=spotify_id), headers=_auth_headers())
    return response.json()


def get_tracks(spotify_ids: list) -> list:
    """Batched track metadata lookup, up to 50 IDs per call (bulk seed runs)."""
    tracks = []
    for i in range(0, len(spotify_ids), 50):
        chunk = spotify_ids[i : i + 50]
        response = _request_with_retry(
            "get", TRACKS_URL, headers=_auth_headers(), params={"ids": ",".join(chunk)}
        )
        tracks.extend(response.json()["tracks"])
    return tracks


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "levitating dua lipa"
    print("token ok:", bool(get_access_token()))
    track = search_track(query)
    print(track)
