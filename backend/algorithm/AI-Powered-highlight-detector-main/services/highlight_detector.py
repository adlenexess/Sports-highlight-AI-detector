"""
highlight_detector.py
----------------------
Orchestrates the full detection + fusion pipeline on a video.

Optimizations:
  - motion, scene, and audio detectors run in parallel
  - replay detector reuses motion + scene cuts (no second full pass)
"""

import time
from concurrent.futures import ThreadPoolExecutor

import cv2

from services import motion_detector
from services import scene_detector
from services import audio_detector
from services import replay_detector
from services import fusion


def get_video_duration(video_path: str) -> float:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    cap.release()
    if frame_count <= 0:
        raise IOError(f"Could not read video duration: {video_path}")
    return float(frame_count / fps)


def analyze_video(video_path: str, sport: str = "generic", threshold: float = 0.45,
                   max_highlights: int = 8, progress_cb=None):
    """
    Run the full detection + fusion pipeline on a video.

    Returns:
        dict with keys: duration, windows, sport
    """
    def report(msg):
        if progress_cb:
            progress_cb(msg)
        print(f"[highlight_detector] {msg}")

    t0 = time.time()
    duration = get_video_duration(video_path)
    report(f"Video duration: {duration:.1f}s")

    report("Running detectors in parallel...")
    with ThreadPoolExecutor(max_workers=3) as pool:
        motion_future = pool.submit(motion_detector.detect, video_path)
        scene_future = pool.submit(scene_detector.analyze, video_path, duration)
        audio_future = pool.submit(audio_detector.detect, video_path)

        motion_scores = motion_future.result()
        scene_result = scene_future.result()
        audio_scores = audio_future.result()

    scene_scores = scene_result["scores"]
    cuts = scene_result["cuts"]

    report("Running replay detector...")
    replay_scores = replay_detector.detect(
        video_path,
        motion_scores=motion_scores,
        cuts=cuts,
    )

    report("Fusing signals...")
    fused = fusion.fuse(
        motion_scores, audio_scores, scene_scores, replay_scores,
        duration, sport=sport,
    )

    windows = fusion.extract_windows(fused, threshold=threshold)

    relax_steps = [threshold - 0.1, threshold - 0.2, 0.15]
    for relaxed in relax_steps:
        if windows:
            break
        report(f"No highlights at threshold, relaxing to {relaxed:.2f}...")
        windows = fusion.extract_windows(fused, threshold=max(relaxed, 0.1))

    windows = windows[:max_highlights]
    windows_chronological = sorted(windows, key=lambda w: w[0])

    report(f"Done in {time.time() - t0:.1f}s. Found {len(windows)} highlight(s).")

    return {
        "duration": duration,
        "windows": windows_chronological,
        "sport": sport,
    }


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sample.mp4"
    sport = sys.argv[2] if len(sys.argv) > 2 else "generic"
    result = analyze_video(path, sport=sport)
    print(result)
