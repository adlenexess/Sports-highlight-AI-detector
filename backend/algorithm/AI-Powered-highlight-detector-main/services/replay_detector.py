"""
replay_detector.py
-------------------
Flags broadcast replay segments using precomputed motion + scene cuts.
"""

from services.scene_detector import get_cut_timestamps
from services.motion_detector import detect as motion_detect


def detect(
    video_path: str,
    min_replay_len: float = 1.5,
    max_replay_len: float = 8.0,
    motion_scores=None,
    cuts=None,
):
    """
    Flag likely replay windows.

    Pass motion_scores and cuts when already computed to avoid re-scanning.
    """
    if cuts is None:
        try:
            cuts = sorted(get_cut_timestamps(video_path))
        except Exception as error:
            print(f"[replay_detector] warning: {error}")
            return []

    if motion_scores is None:
        motion_scores = motion_detect(video_path)

    if not motion_scores or len(cuts) < 2:
        return [(t, 0.0) for t, _ in motion_scores]

    replay_windows = []
    for i in range(len(cuts) - 1):
        start, end = cuts[i], cuts[i + 1]
        gap = end - start
        if min_replay_len <= gap <= max_replay_len:
            segment_motion = [s for t, s in motion_scores if start <= t <= end]
            if segment_motion and (sum(segment_motion) / len(segment_motion)) < 0.35:
                replay_windows.append((start, end))

    scores = []
    for t, _ in motion_scores:
        in_replay = any(start <= t <= end for start, end in replay_windows)
        scores.append((t, 1.0 if in_replay else 0.0))

    return scores


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sample.mp4"
    result = detect(path)
    flagged = sum(1 for _, s in result if s > 0)
    print(f"Flagged {flagged}/{len(result)} samples as replay")
