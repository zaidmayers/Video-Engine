"""Whisper speech-to-text: transcribe TTS audio and produce per-scene SRT files."""

import os


def _seconds_to_srt_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _segments_to_srt(segments: list, time_offset: float = 0.0) -> str:
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _seconds_to_srt_time(seg["start"] + time_offset)
        end = _seconds_to_srt_time(seg["end"] + time_offset)
        text = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def transcribe_scene(audio_path: str, srt_path: str, whisper_model_name: str = "base") -> list:
    """Transcribe audio with Whisper and write an SRT file. Returns segment list."""
    import whisper
    model = whisper.load_model(whisper_model_name)
    result = model.transcribe(audio_path, word_timestamps=False)
    segments = result["segments"]

    srt_content = _segments_to_srt(segments)
    os.makedirs(os.path.dirname(srt_path), exist_ok=True)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return segments


def build_merged_srt(scenes_data: list[dict]) -> str:
    """
    Build a single merged SRT from a list of dicts:
      {"segments": [...], "time_offset": float}
    """
    all_lines = []
    counter = 1
    for sd in scenes_data:
        offset = sd["time_offset"]
        for seg in sd["segments"]:
            start = _seconds_to_srt_time(seg["start"] + offset)
            end = _seconds_to_srt_time(seg["end"] + offset)
            text = seg["text"].strip()
            all_lines.append(f"{counter}\n{start} --> {end}\n{text}\n")
            counter += 1
    return "\n".join(all_lines)


def transcribe_scenes(audio_paths: list[str], output_dir: str, cfg: dict) -> tuple[list[str], str]:
    """
    Transcribe all scene audio files.
    Returns (list of per-scene SRT paths, merged SRT path).
    """
    model_name = cfg["whisper"]["model"]
    srt_paths = []

    # Lazy-load the model once and reuse it
    import whisper
    print(f"  [Whisper] Loading '{model_name}' model...")
    model = whisper.load_model(model_name)

    scenes_data = []
    time_cursor = 0.0

    for i, audio_path in enumerate(audio_paths):
        scene_num = i + 1
        srt_path = os.path.join(output_dir, f"scene{scene_num:02d}", "captions.srt")
        os.makedirs(os.path.dirname(srt_path), exist_ok=True)

        print(f"  [Whisper] Transcribing scene {scene_num}...")
        result = model.transcribe(audio_path, word_timestamps=False)
        segments = result["segments"]

        srt_content = _segments_to_srt(segments)
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        srt_paths.append(srt_path)

        # Compute audio duration for offset tracking
        import soundfile as sf
        info = sf.info(audio_path)
        scenes_data.append({"segments": segments, "time_offset": time_cursor})
        time_cursor += info.duration

    # Merged SRT for the final video
    merged_srt = os.path.join(output_dir, "final", "captions.srt")
    os.makedirs(os.path.dirname(merged_srt), exist_ok=True)
    merged_content = build_merged_srt(scenes_data)
    with open(merged_srt, "w", encoding="utf-8") as f:
        f.write(merged_content)

    return srt_paths, merged_srt
