#!/usr/bin/env python3
"""
Setup script -installs Python dependencies and downloads Flux model weights.

Run once before using run.py:
    python setup.py

For Flux model download you may need a Hugging Face account that has accepted
the FLUX.1-schnell license at https://huggingface.co/black-forest-labs/FLUX.1-schnell
Set HF_TOKEN env var if required:
    set HF_TOKEN=hf_xxxxx
    python setup.py
"""

import os
import subprocess


COMFYUI_BASE = "C:/Users/Zaid/Videos/Comfy Editor"
MODELS_DIR = os.path.join(COMFYUI_BASE, "models")

# Python 3.11 is where torch/whisper/etc. live -use it for all pip installs.
# setup.py itself may be launched with any Python (e.g. 3.14), so we pin 3.11.
PIPELINE_PYTHON = r"C:\Users\Zaid\AppData\Local\Programs\Python\Python311\python.exe"


def _pip(*args: str) -> bool:
    """Run a pip command under the pipeline Python. Returns True on success."""
    cmd = [PIPELINE_PYTHON, "-m", "pip"] + list(args)
    result = subprocess.run(cmd)
    return result.returncode == 0

# Flux model files to download
FLUX_MODELS = [
    {
        "repo_id": "Comfy-Org/flux1-schnell",
        "filename": "flux1-schnell-fp8.safetensors",
        "dest_subdir": "diffusion_models",
        "description": "Flux.1-schnell diffusion model (fp8, ~8 GB)",
    },
    {
        "repo_id": "comfyanonymous/flux_text_encoders",
        "filename": "t5xxl_fp8_e4m3fn.safetensors",
        "dest_subdir": "text_encoders",
        "description": "T5-XXL text encoder (fp8, ~5 GB)",
    },
    {
        "repo_id": "comfyanonymous/flux_text_encoders",
        "filename": "clip_l.safetensors",
        "dest_subdir": "clip",
        "description": "CLIP-L text encoder (~246 MB)",
    },
    {
        "repo_id": "black-forest-labs/FLUX.1-schnell",
        "filename": "ae.safetensors",
        "dest_subdir": "vae",
        "description": "Flux VAE (~335 MB) -requires HF license acceptance",
        "optional": True,
    },
]


# ---------------------------------------------------------------------------
# Install Python packages
# ---------------------------------------------------------------------------

def install_packages():
    packages = [
        "kokoro",
        "kokoro-onnx",
        "onnxruntime",
        "soundfile",
        "pyyaml",
        "requests",
    ]
    print("\n[Setup] Installing Python packages into Python 3.11...")
    print(f"  Using: {PIPELINE_PYTHON}")
    failed = []
    for pkg in packages:
        print(f"  pip install {pkg} ...", end="", flush=True)
        ok = _pip("install", "--prefer-binary", "--quiet", pkg)
        print(" OK" if ok else " FAILED")
        if not ok:
            failed.append(pkg)
    if failed:
        print(f"\n  WARNING: failed to install: {failed}")
        print("  Try manually: python -m pip install " + " ".join(failed))
    else:
        print("  All packages installed.")


# ---------------------------------------------------------------------------
# Download Flux models
# ---------------------------------------------------------------------------

def check_model_exists(dest_subdir: str, filename: str) -> bool:
    dest = os.path.join(MODELS_DIR, dest_subdir, filename)
    return os.path.exists(dest)


def download_model(repo_id: str, filename: str, dest_subdir: str, description: str) -> bool:
    dest_dir = os.path.join(MODELS_DIR, dest_subdir)
    dest_file = os.path.join(dest_dir, filename)

    if os.path.exists(dest_file):
        print(f"  [OK] {filename} -already present")
        return True

    print(f"  Downloading {description}...")
    print(f"    {repo_id}/{filename} -> {dest_dir}")

    try:
        from huggingface_hub import hf_hub_download
        token = os.environ.get("HF_TOKEN") or None
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=dest_dir,
            token=token,
        )
        # hf_hub_download puts a copy in local_dir directly
        print(f"    Saved to {downloaded}")
        return True
    except Exception as e:
        print(f"  [!] Failed to download {filename}: {e}")
        if "401" in str(e) or "403" in str(e) or "gated" in str(e).lower():
            print(
                f"\n  To download {filename} you need to:\n"
                f"  1. Create a Hugging Face account\n"
                f"  2. Accept the license at https://huggingface.co/{repo_id}\n"
                f"  3. Set HF_TOKEN environment variable:\n"
                f"       set HF_TOKEN=hf_your_token_here\n"
                f"  4. Re-run: python setup.py\n"
            )
        return False


def download_flux_models():
    print("\n[Setup] Checking Flux model files...")

    required_ok = 0
    optional_missing = []
    required_total = sum(1 for m in FLUX_MODELS if not m.get("optional"))

    for m in FLUX_MODELS:
        optional = m.get("optional", False)
        dl_kwargs = {k: v for k, v in m.items() if k != "optional"}
        if check_model_exists(m["dest_subdir"], m["filename"]):
            print(f"  [OK] {m['filename']} -already present")
            if not optional:
                required_ok += 1
            continue
        ok = download_model(**dl_kwargs)
        if ok:
            if not optional:
                required_ok += 1
        elif optional:
            optional_missing.append(m["filename"])

    print(f"\n  {required_ok}/{required_total} required Flux model files ready.")
    if optional_missing:
        print(
            "\n  NOTE: Optional model(s) missing (need HF license):\n"
            + "".join(f"    - {f}\n" for f in optional_missing)
            + "  To download:\n"
            "    1. Accept license: https://huggingface.co/black-forest-labs/FLUX.1-schnell\n"
            "    2. Get token: https://huggingface.co/settings/tokens\n"
            "    3. set HF_TOKEN=hf_your_token_here\n"
            "    4. python setup.py\n"
            "  Without ae.safetensors, image generation (Stage 2) will fail.\n"
            "  You can still test video/TTS/captions: python run.py --skip-images\n"
        )


# ---------------------------------------------------------------------------
# Verify LTX models
# ---------------------------------------------------------------------------

def verify_ltxv_models():
    print("\n[Setup] Checking LTX Video 2.3 model files...")
    ltxv_ckpt = os.path.join(MODELS_DIR, "checkpoints", "ltx-2.3-22b-dev-fp8.safetensors")
    ltxv_te = os.path.join(MODELS_DIR, "text_encoders", "gemma_3_12B_it_fp4_mixed.safetensors")

    for label, path in [("LTX checkpoint", ltxv_ckpt), ("Gemma text encoder", ltxv_te)]:
        if os.path.exists(path):
            size_gb = os.path.getsize(path) / 1e9
            print(f"  [OK] {label}: {os.path.basename(path)} ({size_gb:.1f} GB)")
        else:
            print(f"  [!] MISSING {label}: {path}")
            print(
                f"\n  To download LTX 2.3:\n"
                f"  1. LTX checkpoint (fp8): https://huggingface.co/Lightricks/LTX-2.3-fp8\n"
                f"     -> Save to: {os.path.join(MODELS_DIR, 'checkpoints')}\n"
                f"  2. Gemma 3 12B text encoder: https://huggingface.co/Comfy-Org/ltx-2\n"
                f"     -> Save to: {os.path.join(MODELS_DIR, 'text_encoders')}\n"
            )


# ---------------------------------------------------------------------------
# Verify FFmpeg
# ---------------------------------------------------------------------------

def verify_ffmpeg():
    print("\n[Setup] Checking FFmpeg...")
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    if result.returncode == 0:
        version_line = result.stdout.splitlines()[0]
        print(f"  [OK] {version_line}")
    else:
        print("  [!] FFmpeg not found in PATH!")
        print("      Download from https://ffmpeg.org/download.html")


# ---------------------------------------------------------------------------
# Verify Ollama
# ---------------------------------------------------------------------------

def verify_ollama():
    print("\n[Setup] Checking Ollama...")
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        print(f"  [OK] Ollama running. Models: {models}")
        if not any("qwen2.5" in m or "llama" in m for m in models):
            print("  [!] Suggested: ollama pull qwen2.5:7b")
    except Exception as e:
        print(f"  [!] Ollama not reachable: {e}")
        print("      Install from https://ollama.ai and run: ollama pull qwen2.5:7b")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary():
    print("\n" + "=" * 60)
    print("  Setup complete. To run the pipeline:")
    print()
    print("    python run.py")
    print("    python run.py --theme \"a lone explorer in ancient ruins\"")
    print()
    print("  Options:")
    print("    --theme TEXT       Story theme prompt")
    print("    --story-file PATH  Use an existing story.json")
    print("    --skip-images      Skip Flux image generation")
    print("    --skip-video       Skip LTX video generation")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  VIDEO ENGINE -Setup")
    print("=" * 60)

    install_packages()
    verify_ffmpeg()
    verify_ollama()
    verify_ltxv_models()
    download_flux_models()
    print_summary()
