from embedding_client import embed_text
from groq_client import generate_vibe_schema
from lastfm_client import get_top_tags
from pinecone_client import fetch_vector, upsert_vector
from spotify_client import get_track, search_track


def build_song(query: str) -> dict | None:
    """Resolve a song query to its Spotify metadata, building its Pinecone vibe entry if missing."""
    result = search_track(query)
    if result is None:
        return None

    spotify_id = result["id"]

    if fetch_vector(spotify_id) is None:
        artist = result["artists"][0]["name"]
        track = get_track(spotify_id)
        tags = get_top_tags(artist, result["name"])
        schema = generate_vibe_schema(track, tags)
        embedding = embed_text(schema["description"])
        metadata = {
            "name": result["name"],
            "artist": artist,
            "release_year": int(track["album"]["release_date"][:4]),
            **schema,
        }
        upsert_vector(spotify_id, embedding, metadata)

    return result
