import base64
import os

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API = os.environ["GEMINI_API"]

GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

CAPTION_PROMPT = """Describe the mood, atmosphere, and feeling of this image in 1-2 sentences. \
Focus on the emotional tone and setting — is it cozy, chaotic, romantic, melancholic, energetic? \
Don't just list objects you see; describe how the scene feels."""


def describe_image_vibe(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Turn an uploaded image into a short mood/atmosphere description."""
    encoded = base64.b64encode(image_bytes).decode()

    response = requests.post(
        GENERATE_URL,
        params={"key": GEMINI_API},
        json={
            "contents": [
                {
                    "parts": [
                        {"text": CAPTION_PROMPT},
                        {"inline_data": {"mime_type": mime_type, "data": encoded}},
                    ]
                }
            ]
        },
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
