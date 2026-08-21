import json
from pathlib import Path

from embedding_client import embed_text
from groq_client import generate_vibe_schema
from lastfm_client import get_top_tags
from pinecone_client import fetch_vector, upsert_vector
from spotify_client import get_track, search_track

RAW_DATA_FILE = Path("raw_song_data.json")


def _save_raw_data(spotify_id: str, track: dict, tags: list) -> None:
    """Persist the exact Spotify track + Last.fm tags sent to the LLM, keyed by Spotify ID.

    Lets us regenerate a song's description later (e.g. after a prompt change) without
    ever re-fetching from Spotify or Last.fm again.
    """
    data = json.loads(RAW_DATA_FILE.read_text()) if RAW_DATA_FILE.exists() else {}
    data[spotify_id] = {"track": track, "tags": tags}
    RAW_DATA_FILE.write_text(json.dumps(data, indent=2))


def build_from_track(result: dict, track: dict) -> None:
    """Generate the vibe schema for an already-resolved Spotify result/track and upsert it."""
    artist = result["artists"][0]["name"]
    tags = get_top_tags(artist, result["name"])
    _save_raw_data(result["id"], track, tags)
    schema = generate_vibe_schema(track, tags)
    embedding = embed_text(schema["description"])
    images = track["album"].get("images") or []
    metadata = {
        "name": result["name"],
        "artist": artist,
        "release_year": int(track["album"]["release_date"][:4]),
        "album_art": images[0]["url"] if images else None,
        **schema,
    }
    upsert_vector(result["id"], embedding, metadata)


def build_song(query: str) -> dict | None:
    """Resolve a song query to its Spotify metadata, building its Pinecone vibe entry if missing."""
    result = search_track(query)
    if result is None:
        return None

    if fetch_vector(result["id"]) is None:
        track = get_track(result["id"])
        build_from_track(result, track)

    return result
