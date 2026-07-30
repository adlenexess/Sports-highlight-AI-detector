"""
downloader.py
--------------
Lets the user paste a video URL instead of uploading a file from disk.

Handles two cases:
    1. Direct file links (URL ends in .mp4/.mov/.avi/.mkv, or serves a
       video content-type) -> streamed download via `requests`.
    2. Hosted platform links (YouTube, etc.) -> downloaded via `yt-dlp`,
       which resolves the actual stream URL for us.

Both paths return a local file path with the exact same meaning as an
uploaded file, so app.py can hand it straight to
`highlight_detector.analyze_video()` without caring where the video came
from.
"""

import os
import re
import uuid

import requests

DIRECT_VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")
MAX_DOWNLOAD_BYTES = 500 * 1024 * 1024  # 500 MB cap, matches upload limit


def is_probably_direct_file(url: str) -> bool:
    """Heuristic: does the URL path itself end in a known video extension?"""
    path = url.split("?")[0].split("#")[0]
    return path.lower().endswith(DIRECT_VIDEO_EXTENSIONS)


def _safe_name(url: str) -> str:
    stem = re.sub(r"[^a-zA-Z0-9]+", "_", url)[-40:]
    return f"{uuid.uuid4().hex[:8]}_{stem}"


def download_direct(url: str, dest_folder: str) -> str:
    """Stream-download a direct video file link. Returns the local path."""
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "")
        if "video" not in content_type and not is_probably_direct_file(url):
            raise ValueError(
                f"URL does not appear to point to a video file (Content-Type: {content_type})"
            )

        ext = os.path.splitext(url.split("?")[0])[1] or ".mp4"
        filename = _safe_name(url) + ext
        dest_path = os.path.join(dest_folder, filename)

        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                downloaded += len(chunk)
                if downloaded > MAX_DOWNLOAD_BYTES:
                    f.close()
                    os.remove(dest_path)
                    raise ValueError("Video exceeds 500 MB download limit")
                f.write(chunk)

    return dest_path


def download_via_ytdlp(url: str, dest_folder: str) -> str:
    """Download from a hosting platform (YouTube, etc.) using yt-dlp."""
    import yt_dlp

    output_template = os.path.join(dest_folder, _safe_name(url) + ".%(ext)s")

    ydl_opts = {
        "format": "mp4/bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "max_filesize": MAX_DOWNLOAD_BYTES,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
        # merge_output_format can change the extension to .mp4 after download
        if not os.path.exists(filepath):
            root, _ = os.path.splitext(filepath)
            candidate = root + ".mp4"
            if os.path.exists(candidate):
                filepath = candidate

    return filepath


def fetch_video_from_url(url: str, dest_folder: str) -> str:
    """
    Main entry point. Tries the direct-download path first (fast, no extra
    dependency needed), falls back to yt-dlp for hosted platforms.

    Returns:
        Local file path to the downloaded video.
    """
    os.makedirs(dest_folder, exist_ok=True)

    if not url or not url.strip().lower().startswith(("http://", "https://")):
        raise ValueError("Please enter a valid http(s) video URL")

    url = url.strip()

    if is_probably_direct_file(url):
        try:
            return download_direct(url, dest_folder)
        except Exception:
            pass  # fall through to yt-dlp in case it's a redirect/misleading extension

    return download_via_ytdlp(url, dest_folder)


if __name__ == "__main__":
    import sys
    test_url = sys.argv[1]
    path = fetch_video_from_url(test_url, "static/uploads")
    print(f"Downloaded to: {path}")
