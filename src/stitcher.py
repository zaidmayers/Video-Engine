"""FFmpeg pipeline: combine video clips, audio, and burn-in captions into a final video."""

import os
import subprocess
import tempfile


def _run(cmd: list[str], desc: str) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{desc} failed:\n{result.stderr[-3000:]}")


def mix_audio_onto_video(video_path: str, audio_path: str, out_path: str) -> str:
    """Overlay TTS audio onto a video clip. Video loops to fill audio duration."""
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-map", "0:v:0",
        "-map", "1:a:0",
        out_path,
    ]
    _run(cmd, f"audio mix for {os.path.basename(video_path)}")
    return out_path


def concatenate_videos(video_paths: list[str], out_path: str) -> str:
    """Concatenate a list of videos (must share codec/resolution) via FFmpeg concat demuxer."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for p in video_paths:
            abs_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")
        list_path = f.name

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        out_path,
    ]
    try:
        _run(cmd, "video concatenation")
    finally:
        os.unlink(list_path)
    return out_path


def burn_captions(video_path: str, srt_path: str, out_path: str) -> str:
    """Burn SRT captions into the video using FFmpeg subtitles filter."""
    # Escape Windows paths for FFmpeg subtitles filter
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", (
            f"subtitles='{srt_escaped}':force_style='"
            "FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=2'"
        ),
        "-c:a", "copy",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        out_path,
    ]
    _run(cmd, "caption burn-in")
    return out_path


def stitch_final(
    video_paths: list[str],
    audio_paths: list[str],
    srt_path: str,
    out_path: str,
    output_dir: str,
) -> str:
    """
    Full pipeline:
    1. Overlay TTS audio onto each clip
    2. Concatenate all clips
    3. Burn in captions
    """
    mixed_paths = []
    for i, (vpath, apath) in enumerate(zip(video_paths, audio_paths)):
        mixed = os.path.join(output_dir, f"scene{i+1:02d}", "mixed.mp4")
        os.makedirs(os.path.dirname(mixed), exist_ok=True)
        print(f"  [FFmpeg] Mixing audio for scene {i+1}...")
        mixed_paths.append(mix_audio_onto_video(vpath, apath, mixed))

    concat_path = os.path.join(output_dir, "final", "concat.mp4")
    os.makedirs(os.path.dirname(concat_path), exist_ok=True)
    print("  [FFmpeg] Concatenating clips...")
    concatenate_videos(mixed_paths, concat_path)

    print("  [FFmpeg] Burning captions...")
    burn_captions(concat_path, srt_path, out_path)

    os.unlink(concat_path)
    return out_path
