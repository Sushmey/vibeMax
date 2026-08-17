import sys

from build import build_song
from embedding_client import embed_text
from groq_client import interpret_vibe_query
from pinecone_client import fetch_vector, query_vectors

MAX_QUERY_LENGTH = 300


def get_vector_for_song(query: str) -> list | None:
    """Resolve a song query to its stored vector, building it (cold start) if missing."""
    result = build_song(query)
    if result is None:
        return None

    existing = fetch_vector(result["id"])
    return existing["values"] if existing else None


def search(query: str, as_song: bool = False, top_k: int = 5, energy: str | None = None) -> list:
    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(f"That's a bit long — keep it under {MAX_QUERY_LENGTH} characters.")

    if as_song:
        vector = get_vector_for_song(query)
    else:
        interpreted = interpret_vibe_query(query)
        if interpreted is None:
            raise ValueError("Couldn't process that — try rephrasing your prompt.")
        print("interpreted vibe:", interpreted, flush=True)
        vector = embed_text(interpreted["description"])
        # if energy is None:
        #     energy = interpreted.get("energy")

    return query_vectors(vector, top_k=top_k, energy=energy)


def print_results(matches: list) -> None:
    if not matches:
        print("No matches.")
        return

    for match in matches:
        meta = match.get("metadata", {})
        print(f"{match['score']:.3f}  {meta.get('name')} — {meta.get('artist')} ({meta.get('release_year')})")
        print(f"    mood: {meta.get('mood')} | energy: {meta.get('energy')} | era_feel: {meta.get('era_feel')}")
        print(f"    best_for: {meta.get('best_for')}")
        print(f"    {meta.get('description')}")
        print()


if __name__ == "__main__":
    args = sys.argv[1:]
    as_song = "--song" in args
    args = [a for a in args if a != "--song"]
    query = " ".join(args)

    if not query:
        print("Usage: python3 search.py [--song] <vibe phrase or song name>")
        sys.exit(1)

    print_results(search(query, as_song=as_song))
