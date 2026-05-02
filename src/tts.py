"""XTTS-v2 TTS: synthesise narration text to WAV files."""

import os


def _load_model(cfg: dict):
    try:
        import torch
        from TTS.api import TTS
    except ImportError as e:
        raise ImportError(
            "Coqui TTS not installed. Run: pip install TTS\n"
            f"Original error: {e}"
        )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  [TTS] Loading XTTS-v2 on {device}...")
    return TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


def synthesise(text: str, dest_path: str, cfg: dict, tts=None) -> str:
    """Render text to a WAV file using XTTS-v2. Returns dest_path."""
    if tts is None:
        tts = _load_model(cfg)

    speaker = cfg["tts"]["speaker"]
    lang = cfg["tts"]["lang"]

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    tts.tts_to_file(text=text, speaker=speaker, language=lang, file_path=dest_path)
    return dest_path


def synthesise_scenes(scenes: list[dict], output_dir: str, cfg: dict) -> list[str]:
    """Generate TTS audio for each scene. Returns list of WAV paths."""
    tts = _load_model(cfg)
    audio_paths = []
    for scene in scenes:
        n = scene["scene_number"]
        text = scene["narration"]
        dest = os.path.join(output_dir, f"scene{n:02d}", "narration.wav")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"  [TTS] Scene {n}: '{text[:60]}...'")
        path = synthesise(text, dest, cfg, tts=tts)
        audio_paths.append(path)
    return audio_paths
