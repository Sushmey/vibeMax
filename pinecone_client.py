import os

import requests
from dotenv import load_dotenv

load_dotenv()

PINECONE_API = os.environ["PINECONE_API"]
PINECONE_HOST = os.environ["PINECONE_HOST"]

HEADERS = {
    "Api-Key": PINECONE_API,
    "Content-Type": "application/json",
}


def fetch_vector(spotify_id: str) -> dict | None:
    """Look up a stored vector by Spotify ID. None if this song hasn't been seeded/built yet."""
    response = requests.get(
        f"https://{PINECONE_HOST}/vectors/fetch",
        headers=HEADERS,
        params={"ids": spotify_id},
    )
    response.raise_for_status()
    vectors = response.json().get("vectors", {})
    return vectors.get(spotify_id)


def upsert_vector(spotify_id: str, embedding: list, metadata: dict) -> None:
    """Store/overwrite a song's vector + vibe metadata under its Spotify ID."""
    response = requests.post(
        f"https://{PINECONE_HOST}/vectors/upsert",
        headers=HEADERS,
        json={"vectors": [{"id": spotify_id, "values": embedding, "metadata": metadata}]},
    )
    response.raise_for_status()


def query_vectors(embedding: list, top_k: int = 10, energy: str | None = None) -> list:
    """Nearest-neighbor search, optionally filtered by energy (low/medium/high)."""
    body = {"vector": embedding, "topK": top_k, "includeMetadata": True}
    if energy:
        body["filter"] = {"energy": energy}

    response = requests.post(f"https://{PINECONE_HOST}/query", headers=HEADERS, json=body)
    response.raise_for_status()
    return response.json().get("matches", [])
