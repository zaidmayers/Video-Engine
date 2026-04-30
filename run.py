#!/usr/bin/env python3
"""
Video Engine — one-click AI video pipeline.

Story → Flux images → LTX 2.3 video clips → Kokoro TTS → Whisper captions → FFmpeg final video

Usage:
    python run.py
    python run.py --theme "a lone astronaut discovers life on Mars"
    python run.py --story-file my_story.json   # skip story generation
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def resolve_run_dir(base_output: str, story_file: str | None) -> str:
    """Return the run directory to use for this invocation.

    If story_file lives inside an existing runXX folder, resume that run.
    Otherwise create the next runXX folder.
    """
    os.makedirs(base_output, exist_ok=True)
    if story_file:
        abs_story = os.path.abspath(story_file)
        abs_base = os.path.abspath(base_output)
        rel = os.path.relpath(abs_story, abs_base)
        parts = rel.split(os.sep)
        if len(parts) >= 2 and re.match(r"^run\d+$", parts[0]):
            run_dir = os.path.join(base_output, parts[0])
            print(f"  Resuming {parts[0]}/")
            return run_dir

    existing = [
        d for d in os.listdir(base_output)
        if os.path.isdir(os.path.join(base_output, d)) and re.match(r"^run\d+$", d)
    ]
    nums = [int(re.search(r"\d+", d).group()) for d in existing] if existing else [0]
    run_dir = os.path.join(base_output, f"run{max(nums) + 1:02d}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def ensure_comfyui_running(cfg: dict) -> "ComfyClient":
    from src.comfy_api import ComfyClient
    host = cfg["comfyui"]["host"]
    port = cfg["comfyui"]["port"]
    client = ComfyClient(host, port)

    if client.is_ready():
        print("[ComfyUI] Already running.")
        return client

    print("[ComfyUI] Server not detected — attempting to start...")
    python = cfg["comfyui"]["venv_python"]
    main_py = cfg["comfyui"]["main_py"]
    base_dir = cfg["comfyui"]["base_dir"]
    extra_cfg = cfg["comfyui"]["extra_model_paths"]

    cmd = [
        python, main_py,
        "--user-directory", os.path.join(base_dir, "user"),
        "--input-directory", os.path.join(base_dir, "input"),
        "--output-directory", os.path.join(base_dir, "output"),
        "--base-directory", base_dir,
        "--extra-model-paths-config", extra_cfg,
        "--log-stdout",
        "--listen", host,
        "--port", str(port),
        "--enable-manager",
    ]
    print(f"  Running: {' '.join(cmd[:3])} ...")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    print(f"  Started ComfyUI (pid={proc.pid}). Waiting for ready...")
    client.wait_until_ready(timeout=180)
    return client


def scene_dir(output_dir: str, scene_num: int) -> str:
    d = os.path.join(output_dir, f"scene{scene_num:02d}")
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def stage_story(cfg: dict, theme: str | None, story_file: str | None) -> dict:
    print("\n=== Stage 1: Story Generation ===")
    if story_file and os.path.exists(story_file):
        print(f"  Loading story from {story_file}")
        with open(story_file) as f:
            story = json.load(f)
    else:
        from src.story import generate_story, print_story
        story = generate_story(cfg, theme)
        # Save for re-use / inspection
        out = os.path.join(cfg["output_dir"], "story.json")
        os.makedirs(cfg["output_dir"], exist_ok=True)
        with open(out, "w") as f:
            json.dump(story, f, indent=2)
        print_story(story)
        print(f"  Saved to {out}")
    return story


def stage_images(comfy, cfg: dict, story: dict) -> list[str]:
    print("\n=== Stage 2: Flux Image Generation ===")
    from src.image_gen import generate_image
    image_paths = []
    output_dir = cfg["output_dir"]

    for scene in story["scenes"]:
        n = scene["scene_number"]
        dest = os.path.join(scene_dir(output_dir, n), "scene_image.png")
        if os.path.exists(dest):
            print(f"  [Flux] Scene {n}: cached at {dest}")
        else:
            generate_image(comfy, cfg, scene["image_prompt"], dest, n)
        image_paths.append(dest)

    return image_paths


def stage_videos(comfy, cfg: dict, story: dict, image_paths: list[str]) -> list[str]:
    print("\n=== Stage 3: LTX Video Generation ===")
    from src.video_gen import generate_video, extract_last_frame
    video_paths = []
    output_dir = cfg["output_dir"]

    for i, scene in enumerate(story["scenes"]):
        n = scene["scene_number"]
        video_dest = os.path.join(scene_dir(output_dir, n), "clip.mp4")

        # For scenes 2+, use last frame of previous clip as starting image
        if i == 0:
            source_image = image_paths[i]
        else:
            prev_dir = scene_dir(output_dir, n - 1)
            last_frame = os.path.join(prev_dir, "last_frame.png")
            if not os.path.exists(last_frame):
                print(f"  [FFmpeg] Extracting last frame from scene {n-1}...")
                extract_last_frame(video_paths[i - 1], last_frame)
            source_image = last_frame

        if os.path.exists(video_dest):
            print(f"  [LTX] Scene {n}: cached at {video_dest}")
        else:
            generate_video(comfy, cfg, source_image, scene["video_prompt"], video_dest, n)

        video_paths.append(video_dest)

    return video_paths


def stage_tts(cfg: dict, story: dict) -> list[str]:
    print("\n=== Stage 4: TTS Audio Generation ===")
    from src.tts import synthesise_scenes
    return synthesise_scenes(story["scenes"], cfg["output_dir"], cfg)


def stage_captions(cfg: dict, audio_paths: list[str]) -> str:
    print("\n=== Stage 5: Whisper Captioning ===")
    from src.captions import transcribe_scenes
    _, merged_srt = transcribe_scenes(audio_paths, cfg["output_dir"], cfg)
    print(f"  Merged SRT: {merged_srt}")
    return merged_srt


def stage_stitch(cfg: dict, video_paths: list[str], audio_paths: list[str], srt_path: str, story: dict) -> str:
    print("\n=== Stage 6: Final Video Assembly ===")
    from src.stitcher import stitch_final

    title_slug = story["title"].lower().replace(" ", "_")[:40]
    out_path = os.path.join(cfg["output_dir"], f"{title_slug}.mp4")

    stitch_final(video_paths, audio_paths, srt_path, out_path, cfg["output_dir"])
    return out_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AI video pipeline")
    parser.add_argument("--theme", default=None, help="Story theme prompt")
    parser.add_argument("--story-file", default=None, help="Path to existing story.json")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument(
        "--skip-images", action="store_true",
        help="Skip Flux image generation (use existing images in output/sceneXX/scene_image.png)"
    )
    parser.add_argument(
        "--skip-video", action="store_true",
        help="Skip LTX video generation (use existing clips in output/sceneXX/clip.mp4)"
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    run_dir = resolve_run_dir(cfg["output_dir"], args.story_file)
    cfg["output_dir"] = run_dir

    t0 = time.time()
    print("=" * 60)
    print("  VIDEO ENGINE — AI Automated Story Video Pipeline")
    print(f"  Run folder: {run_dir}")
    print("=" * 60)

    # ── Stage 1: Story ──────────────────────────────────────────────
    story = stage_story(cfg, args.theme, args.story_file)

    # ── ComfyUI ─────────────────────────────────────────────────────
    need_comfy = not (args.skip_images and args.skip_video)
    comfy = None
    if need_comfy:
        comfy = ensure_comfyui_running(cfg)

    # ── Stage 2: Images ─────────────────────────────────────────────
    if args.skip_images:
        print("\n=== Stage 2: Flux Images [SKIPPED] ===")
        output_dir = cfg["output_dir"]
        image_paths = [
            os.path.join(output_dir, f"scene{s['scene_number']:02d}", "scene_image.png")
            for s in story["scenes"]
        ]
        missing = [p for p in image_paths if not os.path.exists(p)]
        if missing:
            print(f"  WARNING: missing images: {missing}")
    else:
        image_paths = stage_images(comfy, cfg, story)

    # ── Stage 3: Videos ─────────────────────────────────────────────
    if args.skip_video:
        print("\n=== Stage 3: LTX Videos [SKIPPED] ===")
        output_dir = cfg["output_dir"]
        video_paths = [
            os.path.join(output_dir, f"scene{s['scene_number']:02d}", "clip.mp4")
            for s in story["scenes"]
        ]
    else:
        video_paths = stage_videos(comfy, cfg, story, image_paths)

    # ── Stage 4: TTS ────────────────────────────────────────────────
    audio_paths = stage_tts(cfg, story)

    # ── Stage 5: Captions ───────────────────────────────────────────
    srt_path = stage_captions(cfg, audio_paths)

    # ── Stage 6: Stitch ─────────────────────────────────────────────
    final_path = stage_stitch(cfg, video_paths, audio_paths, srt_path, story)

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  Done in {elapsed/60:.1f} min")
    print(f"  Final video: {final_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
