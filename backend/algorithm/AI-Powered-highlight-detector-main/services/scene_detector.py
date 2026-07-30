"""
scene_detector.py
------------------
Detects camera cuts (scene changes) in the broadcast feed.
"""

from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector


def get_cut_timestamps(video_path: str, threshold: float = 27.0):
    """Return a list of scene-cut timestamps (seconds) using PySceneDetect."""
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()
    return [scene[0].get_seconds() for scene in scene_list[1:]]


def _cuts_to_density_scores(cuts, video_duration: float, window: float = 5.0):
    if not cuts:
        return []

    step = 1.0
    n_points = int(video_duration // step) + 1
    scores = []

    for i in range(n_points):
        t = i * step
        window_start, window_end = t - window / 2, t + window / 2
        cut_count = sum(1 for c in cuts if window_start <= c <= window_end)
        scores.append((t, cut_count))

    return _normalize(scores)


def analyze(video_path: str, video_duration: float, window: float = 5.0):
    """
    Single pass: return raw cuts and per-second density scores together.
    """
    try:
        cuts = get_cut_timestamps(video_path)
    except Exception as error:
        print(f"[scene_detector] warning: {error}")
        cuts = []

    return {
        "cuts": cuts,
        "scores": _cuts_to_density_scores(cuts, video_duration, window),
    }


def detect(video_path: str, video_duration: float, window: float = 5.0):
    """Convert raw cut timestamps into a per-second cut density score."""
    return analyze(video_path, video_duration, window)["scores"]


def _normalize(scores):
    if not scores:
        return scores
    values = [s for _, s in scores]
    max_val = max(values)
    if max_val <= 0:
        return [(t, 0.0) for t, _ in scores]
    return [(t, v / max_val) for (t, v) in scores]


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sample.mp4"
    cuts = get_cut_timestamps(path)
    print(f"Found {len(cuts)} cuts")
