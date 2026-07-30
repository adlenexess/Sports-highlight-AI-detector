"""
motion_detector.py
-------------------
Detects "motion intensity" over time in a sports video.

APPROACH (current, lightweight):
    We sample frames at a fixed rate, convert to grayscale, and measure the
    mean absolute pixel difference between consecutive sampled frames.
    Fast action (goals, fast breaks, sprints, tackles) produces a spike in
    this signal. Idle/broadcast-cutaway moments produce low values.

WHY THIS DESIGN:
    This module exposes ONE function: `detect(video_path, sample_rate)`
    that returns a list of (timestamp_seconds, score) tuples, normalized to
    0-1. Every other detector (audio, scene, replay) returns the exact same
    shape. This is deliberate: fusion.py just fuses lists of (t, score)
    tuples, so tomorrow you can rip this file out and drop in a YOLOv8-based
    detector (score = number of players/ball movement between frames)
    WITHOUT touching fusion.py, highlight_detector.py, or app.py.

    To upgrade later: replace the body of `detect()` with a YOLO inference
    loop that computes optical-flow-of-detected-objects instead of raw pixel
    diff, but keep the return signature identical.
"""

import cv2
import numpy as np


def detect(video_path: str, sample_rate: float = 2.0):
    """
    Compute motion intensity over time.

    Args:
        video_path: path to the input video file.
        sample_rate: how many frames per second to analyze (lower = faster,
                     higher = more precise). 2.0 is a good default for
                     sports footage.

    Returns:
        List[Tuple[float, float]]: (timestamp_in_seconds, motion_score 0-1)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_interval = max(int(round(fps / sample_rate)), 1)

    scores = []
    prev_gray = None
    frame_idx = 0

    while True:
        if frame_idx % frame_interval == 0:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 180))
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)
                motion_amount = float(np.mean(thresh)) / 255.0
                timestamp = frame_idx / fps
                scores.append((timestamp, motion_amount))

            prev_gray = gray
        else:
            if not cap.grab():
                break

        frame_idx += 1

    cap.release()

    scores = _normalize(scores)
    return scores


def _normalize(scores):
    if not scores:
        return scores
    values = np.array([s for _, s in scores])
    max_val = values.max()
    if max_val <= 0:
        return [(t, 0.0) for t, _ in scores]
    return [(t, float(v / max_val)) for (t, v) in scores]


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "sample.mp4"
    result = detect(path)
    print(f"Analyzed {len(result)} samples")
    for t, s in result[:10]:
        print(f"  t={t:.1f}s  motion={s:.3f}")
