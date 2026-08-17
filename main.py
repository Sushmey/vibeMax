from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from search import search

app = FastAPI(title="vibeMax API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    as_song: bool = False
    energy: Optional[str] = None
    top_k: int = 10


class Match(BaseModel):
    score: float
    name: Optional[str] = None
    artist: Optional[str] = None
    release_year: Optional[int] = None
    mood: Optional[str] = None
    energy: Optional[str] = None
    era_feel: Optional[str] = None
    best_for: Optional[str] = None
    description: Optional[str] = None


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/search", response_model=list[Match])
def search_endpoint(request: SearchRequest):
    matches = search(request.query, as_song=request.as_song, top_k=request.top_k, energy=request.energy)
    return [Match(score=match["score"], **match.get("metadata", {})) for match in matches]
