"""Generate a short story script with per-scene image/video/narration prompts via Ollama."""

import json
import re
import requests


STORY_SYSTEM = """\
You are a cinematic story writer and visual director. Generate a short story for an AI video pipeline.
Each scene must have three fields:

image_prompt: Extremely detailed photorealistic description for Flux image generation. Include:
  - Subject: precise physical description (species, markings, color, size, posture, expression)
  - Environment: specific setting details (type of jungle/terrain, time of day, weather, foliage)
  - Lighting: exact light quality (dappled moonlight, shaft of golden sunlight, blue twilight)
  - Camera: angle and framing (low-angle wide shot, tight close-up, eye-level mid-shot)
  - Mood: atmosphere and color palette
  Write as a dense comma-separated prompt, not sentences. At least 60 words.

video_prompt: Motion description for LTX video generation. Include:
  - Exactly what moves and how (slow predatory footstep, sudden burst forward, tail swishing)
  - Camera movement (slow push in, lateral tracking, handheld shake, static locked)
  - Environmental motion (leaves rustling, water rippling, shadows shifting)
  - Pace and feel (tense and still, explosive and fast, calm and majestic)
  Write as a dense comma-separated prompt, not sentences. At least 40 words.

narration: 1-2 short sentences of spoken voiceover. Plain prose, no quotes, no stage directions.

The video_prompt for scenes 2+ should continue naturally from the previous scene's ending frame.

Respond ONLY with valid JSON (no markdown, no extra text):
{
  "title": "Story Title",
  "scenes": [
    {
      "scene_number": 1,
      "image_prompt": "...",
      "video_prompt": "...",
      "narration": "..."
    }
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
