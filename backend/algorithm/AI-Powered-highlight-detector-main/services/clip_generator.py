"""
clip_generator.py
------------------
Renders highlight.mp4 using ffmpeg with stream-copy when possible and
parallel segment extraction.
"""

import os
import subprocess
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
MAX_SEGMENT_WORKERS = 4


def _run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [FFMPEG, *args],
        capture_output=True,
        text=True,
    )


def _extract_segment(video_path: str, start: float, duration: float, segment_path: str) -> str:
    """Try fast stream copy first; fall back to ultrafast re-encode."""
    copy_result = _run_ffmpeg([
        "-y",
        "-ss", f"{start:.3f}",
        "-i", video_path,
        "-t", f"{duration:.3f}",
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        segment_path,
    ])
    if (
        copy_result.returncode == 0
        and os.path.exists(segment_path)
        and os.path.getsize(segment_path) > 0
    ):
        return segment_path

    encode_result = _run_ffmpeg([
        "-y",
        "-ss", f"{start:.3f}",
        "-i", video_path,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-c:a", "aac",
        "-movflags", "+faststart",
        segment_path,
    ])
    if encode_result.returncode != 0:
        detail = (encode_result.stderr or encode_result.stdout or "ffmpeg failed").strip()
        raise RuntimeError(detail[-500:])
    return segment_path


def generate_highlight_video(video_path: str, windows, output_path: str,
                              crossfade: float = 0.5):
    del crossfade

    if not windows:
        raise ValueError("No highlight windows to render")

    segments: list[tuple[int, str]] = []
    list_file = os.path.join(tempfile.gettempdir(), f"sportslab_{uuid.uuid4().hex}.txt")

    try:
        jobs = []
        for index, (start, end, _score) in enumerate(windows):
            start = max(0.0, float(start))
            end = max(start + 0.5, float(end))
            duration = end - start
            segment_path = os.path.join(
                tempfile.gettempdir(),
                f"sportslab_{uuid.uuid4().hex}.mp4",
            )
            jobs.append((index, start, duration, segment_path))

        workers = min(MAX_SEGMENT_WORKERS, max(1, len(jobs)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_extract_segment, video_path, start, duration, path): (index, path)
                for index, start, duration, path in jobs
            }
            for future in as_completed(futures):
                index, path = futures[future]
                future.result()
                segments.append((index, path))

        segments.sort(key=lambda item: item[0])
        temp_segments = [path for _, path in segments]

        if not temp_segments:
            raise ValueError("All highlight windows were too short after clamping")

        with open(list_file, "w", encoding="utf-8") as handle:
            for segment in temp_segments:
                safe_path = os.path.abspath(segment).replace("\\", "/")
                handle.write(f"file '{safe_path}'\n")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        if len(temp_segments) == 1:
            concat_args = ["-y", "-i", temp_segments[0], "-c", "copy", output_path]
        else:
            concat_args = [
                "-y", "-f", "concat", "-safe", "0",
                "-i", list_file, "-c", "copy", output_path,
            ]

        concat_result = _run_ffmpeg(concat_args)
        if concat_result.returncode != 0:
            detail = (concat_result.stderr or concat_result.stdout or "ffmpeg failed").strip()
            raise RuntimeError(detail[-500:])
    finally:
        for _, segment in segments:
            if os.path.exists(segment):
                try:
                    os.remove(segment)
                except OSError:
                    pass
        if os.path.exists(list_file):
            try:
                os.remove(list_file)
            except OSError:
                pass

    return output_path


if __name__ == "__main__":
    import sys
    from services.highlight_detector import analyze_video

    path = sys.argv[1] if len(sys.argv) > 1 else "sample.mp4"
    result = analyze_video(path)
    out = generate_highlight_video(path, result["windows"], "output/highlight.mp4")
    print(f"Wrote {out}")
