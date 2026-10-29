import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate_scene_video(prompt: str, output_path: str, aspect_ratio: str = "9:16") -> str:
    """Generates a video scene using Google's Veo model and saves the .mp4 locally."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Map UI aspect ratio selection to API format
    ar_format = "9:16" if "9:16" in aspect_ratio else "16:9"

    print(f"Generating scene with prompt: {prompt}")

    # Initiate video generation job using active Veo model
    operation = client.models.generate_videos(
        model="veo-3.1-fast-generate-preview",  # <-- UPDATED MODEL NAME
        prompt=prompt,
        config=types.GenerateVideosConfig(
            person_generation="DONT_ALLOW",
            aspect_ratio=ar_format,
            duration_seconds=6,
        ),
    )

    # Poll until video generation completes
    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)

    # Save the resulting MP4
    result = operation.result
    for generated_video in result.generated_videos:
        with open(output_path, "wb") as f:
            f.write(generated_video.video.video_bytes)
        return output_path

    raise Exception("Video generation completed, but no video file was returned.")