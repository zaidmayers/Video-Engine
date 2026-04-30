"""Flux text-to-image via ComfyUI API."""

import copy
import json
import os
import random


def _load_workflow(workflow_path: str) -> dict:
    with open(workflow_path) as f:
        return json.load(f)


def build_flux_workflow(cfg: dict, prompt: str, output_prefix: str, seed: int | None = None) -> dict:
    workflow_path = os.path.join(os.path.dirname(__file__), "..", "workflows", "flux_t2i.json")
    wf = _load_workflow(workflow_path)

    seed = seed if seed is not None else random.randint(0, 2**31)
    w = cfg["image"]["width"]
    h = cfg["image"]["height"]
    steps = cfg["image"]["steps"]
    guidance = cfg["image"]["guidance"]
    models = cfg["models"]

    # Substitute template values
    wf["1"]["inputs"]["unet_name"] = models["flux_unet"]
    wf["2"]["inputs"]["clip_name1"] = models["flux_t5"]
    wf["2"]["inputs"]["clip_name2"] = models["flux_clip"]
    wf["3"]["inputs"]["vae_name"] = models["flux_vae"]
    wf["4"]["inputs"]["clip_l"] = prompt
    wf["4"]["inputs"]["t5xxl"] = prompt
    wf["4"]["inputs"]["guidance"] = guidance
    wf["5"]["inputs"]["width"] = w
    wf["5"]["inputs"]["height"] = h
    wf["6"]["inputs"]["noise_seed"] = seed
    wf["9"]["inputs"]["steps"] = steps
    wf["12"]["inputs"]["filename_prefix"] = output_prefix

    return wf


def generate_image(comfy, cfg: dict, prompt: str, dest_path: str, scene_idx: int) -> str:
    """Generate a Flux image for the given prompt and save to dest_path."""
    prefix = f"flux/scene{scene_idx:02d}"
    seed = cfg["image"]["seed"] + scene_idx
    workflow = build_flux_workflow(cfg, prompt, prefix, seed=seed)

    print(f"  [Flux] Generating image for scene {scene_idx}...")
    return comfy.run_workflow(workflow, dest_path, timeout=600)
