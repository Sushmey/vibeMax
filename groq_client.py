import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API = os.environ["GROQ_API"]

CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a music vibe analyst. Given metadata and community tags for a song, \
output a JSON object describing its vibe with exactly these fields:

- "mood": 2-3 adjectives capturing the emotional tone (e.g. "wistful, defiant")
- "energy": one of "low", "medium", "high"
- "era_feel": the decade the song sonically evokes (e.g. "1980s"), which may differ from its actual release year
- "best_for": a short occasion or setting phrase (e.g. "late-night drive")
- "description": 1-2 evocative sentences capturing the actual vibe of the song

Respond with only the JSON object, no other text."""


def generate_vibe_schema(track: dict, tags: list) -> dict:
    """Build the vibe schema for a song from its Spotify track data and Last.fm tags."""
    artist_names = ", ".join(artist["name"] for artist in track["artists"])
    facts = (
        f"Track: {track['name']}\n"
        f"Artist(s): {artist_names}\n"
        f"Album: {track['album']['name']}\n"
        f"Release date: {track['album']['release_date']}\n"
        f"Popularity: {track.get('popularity', 'unknown')}\n"
        f"Last.fm tags: {', '.join(tags) if tags else 'none'}"
    )

    response = requests.post(
        CHAT_URL,
        headers={"Authorization": f"Bearer {GROQ_API}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": facts},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
        },
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


if __name__ == "__main__":
    from lastfm_client import get_top_tags
    from spotify_client import get_track, search_track

    result = search_track("levitating dua lipa")
    track = get_track(result["id"])
    tags = get_top_tags(track["artists"][0]["name"], track["name"])
    print(generate_vibe_schema(track, tags))
