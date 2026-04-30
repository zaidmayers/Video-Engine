"""Kokoro TTS: synthesise narration text to WAV files."""

import os
import re


def synthesise(text: str, dest_path: str, cfg: dict) -> str:
    """Render text to a WAV file using Kokoro. Returns dest_path."""
    try:
        import soundfile as sf
        from kokoro import KPipeline
    except ImportError as e:
        raise ImportError(
            "Kokoro not installed. Run: pip install kokoro soundfile\n"
            f"Original error: {e}"
        )

    voice = cfg["tts"]["voice"]
    speed = cfg["tts"]["speed"]
    lang = cfg["tts"]["lang"]

    pipeline = KPipeline(lang_code=lang)

    # Collect all audio chunks
    audio_chunks = []
    sample_rate = 24000

    for _, _, audio in pipeline(text, voice=voice, speed=speed):
        audio_chunks.append(audio)

    if not audio_chunks:
        raise RuntimeError("Kokoro produced no audio output")

    import numpy as np
    combined = np.concatenate(audio_chunks)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    sf.write(dest_path, combined, sample_rate)
    return dest_path


def synthesise_scenes(scenes: list[dict], output_dir: str, cfg: dict) -> list[str]:
    """Generate TTS audio for each scene. Returns list of WAV paths."""
    audio_paths = []
    for scene in scenes:
        n = scene["scene_number"]
        text = scene["narration"]
        dest = os.path.join(output_dir, f"scene{n:02d}", "narration.wav")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"  [TTS] Scene {n}: '{text[:60]}...'")
        path = synthesise(text, dest, cfg)
        audio_paths.append(path)
    return audio_paths
