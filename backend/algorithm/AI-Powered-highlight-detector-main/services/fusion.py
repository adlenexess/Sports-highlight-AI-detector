"""
fusion.py
---------
Combines the independent (timestamp, score) signals from motion, audio,
scene-cut-density, and replay detectors into a single "excitement curve",
then extracts highlight time windows from the peaks of that curve.

DESIGN:
    Every detector module returns List[Tuple[float, float]] on its own time
    grid. This module first resamples everything onto one common 1-second
    grid (`_resample`), then combines with tunable weights. This is the
    ONLY file that needs to change if you want to re-balance which signal
    matters most for a given sport (e.g. cricket relies more on commentary/
    audio + replays; football relies more on motion + cuts).
"""

import numpy as np

# Default fusion weights -- tune per sport if desired.
DEFAULT_WEIGHTS = {
    "motion": 0.35,
    "audio": 0.35,
    "scene": 0.15,
    "replay": 0.15,
}

# Per-sport weight presets (used by highlight_detector.py)
SPORT_WEIGHTS = {
    "football": {"motion": 0.40, "audio": 0.30, "scene": 0.15, "replay": 0.15},
    "cricket":  {"motion": 0.20, "audio": 0.40, "scene": 0.15, "replay": 0.25},
    "basketball": {"motion": 0.40, "audio": 0.30, "scene": 0.20, "replay": 0.10},
    "tennis":   {"motion": 0.25, "audio": 0.40, "scene": 0.15, "replay": 0.20},
    "generic":  DEFAULT_WEIGHTS,
}


def _resample(signal, duration, step=1.0):
    """Resample a (t, score) list onto a fixed 1-second grid via nearest neighbor."""
    n_points = int(duration // step) + 1
    grid = np.zeros(n_points)
    if not signal:
        return grid

    times = np.array([t for t, _ in signal])
    values = np.array([v for _, v in signal])

    for i in range(n_points):
        t = i * step
        idx = np.argmin(np.abs(times - t))
        grid[i] = values[idx]

    return grid


def fuse(motion, audio, scene, replay, duration, sport: str = "generic"):
    """
    Fuse all detector signals into one excitement curve.

    Returns:
        np.ndarray of shape (n_seconds,), the fused excitement score
        per second of video, in [0, 1].
    """
    weights = SPORT_WEIGHTS.get(sport, DEFAULT_WEIGHTS)

    m = _resample(motion, duration)
    a = _resample(audio, duration)
    s = _resample(scene, duration)
    r = _resample(replay, duration)

    fused = (
        weights["motion"] * m
        + weights["audio"] * a
        + weights["scene"] * s
        + weights["replay"] * r
    )

    # smooth with a small moving average to avoid single-frame spikes
    fused = _smooth(fused, window=3)
    return fused


def _smooth(arr, window=3):
    if len(arr) < window:
        return arr
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same")


def extract_windows(fused_scores, threshold=0.45, pre_pad=4.0, post_pad=6.0,
                     min_gap=3.0, max_clip_duration=25.0):
    """
    Turn a fused excitement curve into a list of highlight windows.

    Args:
        fused_scores: np.ndarray, one value per second (index = second).
        threshold: minimum score to count as "exciting".
        pre_pad: seconds of context to include BEFORE a peak.
        post_pad: seconds of context to include AFTER a peak.
        min_gap: merge two windows if they're closer than this (seconds).
        max_clip_duration: hard cap on a single highlight's length.

    Returns:
        List[Tuple[float, float, float]]: (start, end, peak_score)
    """
    peak_indices = np.where(fused_scores >= threshold)[0]
    if len(peak_indices) == 0:
        return []

    raw_windows = []
    for idx in peak_indices:
        start = max(0, idx - pre_pad)
        end = idx + post_pad
        score = fused_scores[idx]
        raw_windows.append([start, end, score])

    # merge overlapping / nearby windows
    raw_windows.sort(key=lambda w: w[0])
    merged = [raw_windows[0]]
    for start, end, score in raw_windows[1:]:
        last = merged[-1]
        if start - last[1] <= min_gap:
            last[1] = max(last[1], end)
            last[2] = max(last[2], score)
        else:
            merged.append([start, end, score])

    # enforce max duration by trimming from the tail
    final = []
    for start, end, score in merged:
        if end - start > max_clip_duration:
            end = start + max_clip_duration
        final.append((float(start), float(end), float(score)))

    # rank most exciting first (useful for a "top N highlights" mode)
    final.sort(key=lambda w: w[2], reverse=True)
    return final
