"""
audio_detector.py
------------------
Detects crowd excitement (cheering, whistles, commentator pitch rise) from
the audio track of the match.
"""

import os
import subprocess
import tempfile
import uuid

import imageio_ffmpeg
import librosa
import numpy as np

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def _extract_audio(video_path: str) -> str:
    """Extract audio track to a temporary WAV file. Returns the wav path."""
    wav_path = os.path.join(tempfile.gettempdir(), f"sportslab_{uuid.uuid4().hex}.wav")
    result = subprocess.run(
        [
            FFMPEG,
            "-y",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "22050",
            "-ac",
            "1",
            wav_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not os.path.exists(wav_path):
        raise ValueError("Video has no audio track")
    return wav_path


def detect(video_path: str, hop_seconds: float = 1.0):
    """
    Compute an audio "excitement" score over time.

    Returns:
        List[Tuple[float, float]]: (timestamp_seconds, excitement_score 0-1)
    """
    try:
        wav_path = _extract_audio(video_path)
    except ValueError:
        return []

    try:
        y, sr = librosa.load(wav_path, sr=22050, mono=True)

        hop_length = int(sr * hop_seconds)
        frame_length = hop_length * 2

        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

        n = min(len(rms), len(onset_env))
        rms, onset_env = rms[:n], onset_env[:n]

        rms_norm = _normalize_array(rms)
        onset_norm = _normalize_array(onset_env)

        combined = 0.6 * rms_norm + 0.4 * onset_norm

        timestamps = np.arange(n) * hop_seconds
        return list(zip(timestamps.tolist(), combined.tolist()))
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


def _normalize_array(arr: np.ndarray) -> np.ndarray:
    if arr.size == 0:
        return arr
    max_val = arr.max()
    if max_val <= 0:
        return np.zeros_like(arr)
    return arr / max_val


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sample.mp4"
    result = detect(path)
    print(f"Analyzed {len(result)} audio samples")
    for t, s in result[:10]:
        print(f"  t={t:.1f}s  excitement={s:.3f}")
