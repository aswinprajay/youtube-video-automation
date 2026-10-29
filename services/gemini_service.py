import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Define strict structured schema
class NurseryRhymeResponse(BaseModel):
    lyrics: str = Field(description="The complete structured song lyrics with stanzas and performance cues for Suno AI.")
    scene_prompts: list[str] = Field(description="List of exact visual prompts tailored for Google Flow / Veo, matching each stanza in sequence.")
    suggested_title: str = Field(description="A catchy, high-CTR YouTube title suitable for toddlers and parents.")

def generate_nursery_content(
    character_type: str,
    character_desc: str,
    base_story: str,
    visual_style: str,
    aspect_ratio: str,
    mood: str,
    bpm: int,
    scene_count: int
) -> dict:
    """Calls Gemini to produce structured lyrics, titles, and exact visual prompts."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    system_instruction = (
        "You are an expert children's content creator, songwriter, and 3D visual director. "
        "Your task is to write fun, repetitive, and educational nursery rhymes for toddlers, "
        "and craft highly specific, cinematic visual prompts for Google Flow/Veo video models. "
        "Ensure prompt visual continuity across all scenes (character features, color palette, lighting)."
    )

    user_prompt = f"""
    Create a complete nursery rhyme video package with the following specifications:
    - Character Category: {character_type}
    - Character Details: {character_desc}
    - Core Storyline: {base_story}
    - Visual Art Style: {visual_style}
    - Aspect Ratio: {aspect_ratio}
    - Vibe / Mood: {mood}
    - Target Tempo: {bpm} BPM
    - Number of Scenes: {scene_count}

    Requirements:
    1. The lyrics must have exactly {scene_count} stanzas/sections, formatted clearly with style tags (e.g., [Verse 1], [Chorus]) for Suno AI.
    2. Provide exactly {scene_count} detailed scene prompts for Google Flow/Veo.
    3. Each visual prompt must enforce character consistency and include camera framing, action, lighting, and aspect ratio ({aspect_ratio}).
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=NurseryRhymeResponse,
            temperature=0.7,
        ),
    )

    return json.loads(response.text)