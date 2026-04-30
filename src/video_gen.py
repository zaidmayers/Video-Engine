"""LTX Video 2.3 image-to-video via ComfyUI API."""

import json
import os
import random
import subprocess


def _load_workflow(workflow_path: str) -> dict:
    with open(workflow_path) as f:
        return json.load(f)


def _frame_count_for_duration(duration_seconds: float, fps: int) -> int:
    """Return the nearest valid LTX frame count (must be 9 + n*8) for the given duration."""
    target = int(duration_seconds * fps)
    # Find nearest valid value: 9 + n*8
    n = max(0, round((target - 9) / 8))
    return 9 + n * 8


def build_ltxv_workflow(
    cfg: dict,
    prompt: str,
    uploaded_image_name: str,
    output_prefix: str,
    seed: int | None = None,
) -> dict:
    workflow_path = os.path.join(os.path.dirname(__file__), "..", "workflows", "ltxv_i2v.json")
    wf = _load_workflow(workflow_path)

    seed = seed if seed is not None else random.randint(0, 2**31)
    fps = cfg["video"]["fps"]
    duration = cfg["video"]["duration_seconds"]
    length = _frame_count_for_duration(duration, fps)
    w = cfg["video"]["width"]
    h = cfg["video"]["height"]
    cfg_val = cfg["video"]["cfg"]
    models = cfg["models"]

    ckpt = models["ltxv_checkpoint"]
    te = models["ltxv_text_encoder"]
    lora = models["ltxv_lora"]

    # Model/encoder nodes
    wf["1"]["inputs"]["ckpt_name"] = ckpt
    wf["2"]["inputs"]["text_encoder"] = te
    wf["2"]["inputs"]["ckpt_name"] = ckpt
    wf["10"]["inputs"]["ckpt_name"] = ckpt
    wf["22"]["inputs"]["lora_name"] = lora

    # Prompts
    wf["3"]["inputs"]["text"] = prompt

    # Image
    wf["6"]["inputs"]["image"] = uploaded_image_name

    # Latent dimensions
    wf["8"]["inputs"]["width"] = w
    wf["8"]["inputs"]["height"] = h
    wf["8"]["inputs"]["length"] = length

    # Audio latent length must match
    wf["11"]["inputs"]["frames_number"] = length
    wf["11"]["inputs"]["frame_rate"] = fps

    # Sampling
    wf["13"]["inputs"]["cfg"] = cfg_val
    wf["14"]["inputs"]["noise_seed"] = seed

    # Output prefix
    wf["21"]["inputs"]["filename_prefix"] = output_prefix

    return wf


def generate_video(comfy, cfg: dict, image_path: str, prompt: str, dest_path: str, scene_idx: int) -> str:
    """Upload image, run LTX workflow, save video to dest_path."""
    print(f"  [LTX] Uploading image for scene {scene_idx}...")
    uploaded_name = comfy.upload_image(image_path)

    prefix = f"ltxv/scene{scene_idx:02d}"
    seed = cfg["video"]["seed"] + scene_idx
    workflow = build_ltxv_workflow(cfg, prompt, uploaded_name, prefix, seed=seed)

    print(f"  [LTX] Generating video for scene {scene_idx} ({cfg['video']['duration_seconds']}s at {cfg['video']['fps']}fps)...")
    return comfy.run_workflow(workflow, dest_path, timeout=3600)


def extract_last_frame(video_path: str, frame_path: str) -> str:
    """Extract the last frame of a video using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-sseof", "-1",          # seek 1s before end
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        frame_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg frame extraction failed:\n{result.stderr}")
    return frame_path
