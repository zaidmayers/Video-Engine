"""Generate a short story script with per-scene image/video/narration prompts via Ollama."""

import json
import re
import requests


STORY_SYSTEM = """\
You are a cinematic story writer. Generate a short 4-scene story for an AI video pipeline.
Each scene must have three fields:
- image_prompt: a detailed, vivid visual description for Flux image generation (photorealistic, cinematic)
- video_prompt: a motion description for LTX video animation, describing exactly how the scene moves
- narration: 2-3 sentences of narrator text to be spoken as TTS voiceover (no quotes, plain prose)

The video_prompt for scenes 2, 3, and 4 should naturally continue from the previous scene's ending.

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{
  "title": "Story Title",
  "scenes": [
    {
      "scene_number": 1,
      "image_prompt": "...",
      "video_prompt": "...",
      "narration": "..."
    },
    ...
  ]
}
"""


def generate_story(cfg: dict, theme: str | None = None) -> dict:
    ollama_host = cfg["story"]["ollama_host"]
    model = cfg["story"]["ollama_model"]
    num_scenes = cfg["story"]["num_scenes"]

    user_msg = f"Create a {num_scenes}-scene cinematic story"
    if theme:
        user_msg += f" about: {theme}"
    else:
        user_msg += " (choose any compelling theme — action, drama, sci-fi, nature, etc.)"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": STORY_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
        "options": {"temperature": 0.85},
    }

    print(f"  Generating story with {model}...")
    r = requests.post(f"{ollama_host}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    content = r.json()["message"]["content"].strip()

    # Strip markdown fences if present
    content = re.sub(r"^```(?:json)?\n?", "", content)
    content = re.sub(r"\n?```$", "", content.strip())

    try:
        story = json.loads(content)
    except json.JSONDecodeError as e:
        # Try extracting JSON from the response
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            story = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse story JSON: {e}\nResponse:\n{content}")

    scenes = story.get("scenes", [])
    if len(scenes) != num_scenes:
        raise ValueError(f"Expected {num_scenes} scenes, got {len(scenes)}")

    return story


def print_story(story: dict) -> None:
    print(f"\n  Title: {story['title']}")
    for s in story["scenes"]:
        n = s["scene_number"]
        print(f"\n  Scene {n}:")
        print(f"    Narration : {s['narration'][:80]}...")
        print(f"    Image     : {s['image_prompt'][:80]}...")
        print(f"    Video     : {s['video_prompt'][:80]}...")
