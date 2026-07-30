"""
SportsLab integration gateway.

Serves the SportsLab UI unchanged from disk, injects integration/wire.js at
serve time, and exposes a JSON API that calls the AI highlight detector
backend services directly. Completed runs are logged to SQLite
(databaseSportslab).

Run from the SportsLab project root:
    python integration/gateway.py
"""

from __future__ import annotations

import os
import sys
import time
import uuid
import mimetypes
import tempfile

import imageio_ffmpeg
from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
INTEGRATION_DIR = os.path.dirname(os.path.abspath(__file__))
SPORTSLAB_ROOT = os.path.dirname(INTEGRATION_DIR)
BACKEND_DIR = os.path.join(
    SPORTSLAB_ROOT, "backend", "algorithm", "AI-Powered-highlight-detector-main"
)
DATABASE_DIR = os.path.join(SPORTSLAB_ROOT, "databaseSportslab")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if DATABASE_DIR not in sys.path:
    sys.path.insert(0, DATABASE_DIR)

os.environ.setdefault("IMAGEIO_FFMPEG_EXE", imageio_ffmpeg.get_ffmpeg_exe())
os.environ.setdefault("TEMP", tempfile.gettempdir())
os.environ.setdefault("TMP", tempfile.gettempdir())

from services.highlight_detector import analyze_video  # noqa: E402
from services.clip_generator import generate_highlight_video  # noqa: E402
from services import downloader  # noqa: E402
from persistence import init_db, save_generation_run  # noqa: E402

UPLOAD_FOLDER = os.path.join(BACKEND_DIR, "static", "uploads")
OUTPUT_FOLDER = os.path.join(BACKEND_DIR, "static", "outputs")
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv"}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

init_db()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

WIRE_SCRIPT_TAG = '<script src="/integration/wire.js"></script>'
INJECT_BEFORE = '<script src="js/app.js"></script>'


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def inject_wire_script(html: str) -> str:
    if WIRE_SCRIPT_TAG in html:
        return html
    if INJECT_BEFORE in html:
        return html.replace(INJECT_BEFORE, INJECT_BEFORE + "\n  " + WIRE_SCRIPT_TAG)
    return html.replace("</body>", "  " + WIRE_SCRIPT_TAG + "\n</body>")


@app.route("/")
def sportslab_index():
    index_path = os.path.join(SPORTSLAB_ROOT, "index.html")
    with open(index_path, encoding="utf-8") as f:
        html = f.read()
    return Response(inject_wire_script(html), mimetype="text/html; charset=utf-8")


@app.route("/integration/wire.js")
def serve_wire_js():
    return send_from_directory(INTEGRATION_DIR, "wire.js", mimetype="application/javascript")


@app.route("/<path:asset_path>")
def serve_sportslab_static(asset_path: str):
    if asset_path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404

    full_path = os.path.join(SPORTSLAB_ROOT, asset_path)
    if not os.path.isfile(full_path):
        return jsonify({"error": "Not found"}), 404

    directory, filename = os.path.split(full_path)
    mimetype = mimetypes.guess_type(filename)[0]
    return send_from_directory(directory, filename, mimetype=mimetype)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    sport = request.form.get("sport", "cricket")
    if sport not in {"football", "cricket", "basketball", "tennis", "generic"}:
        sport = "cricket"

    source_mode = request.form.get("source_mode", "file")
    unique_id = uuid.uuid4().hex[:8]
    saved_path = None
    original_filename = None

    try:
        if source_mode == "url":
            video_url = request.form.get("video_url", "").strip()
            if not video_url:
                return jsonify({"success": False, "error": "Please paste a video URL."}), 400
            saved_path = downloader.fetch_video_from_url(video_url, UPLOAD_FOLDER)
            original_filename = os.path.basename(saved_path)
        else:
            if "video" not in request.files:
                return jsonify({"success": False, "error": "No video file provided."}), 400

            file = request.files["video"]
            if not file or file.filename == "":
                return jsonify({"success": False, "error": "No file selected."}), 400
            if not allowed_file(file.filename):
                return jsonify(
                    {"success": False, "error": "Unsupported file type. Use mp4, mov, avi, or mkv."}
                ), 400

            original_filename = secure_filename(file.filename)
            saved_name = f"{unique_id}_{original_filename}"
            saved_path = os.path.join(UPLOAD_FOLDER, saved_name)
            file.save(saved_path)

        t0 = time.time()
        result = analyze_video(saved_path, sport=sport)
        output_filename = f"highlight_{unique_id}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        generate_highlight_video(saved_path, result["windows"], output_path)
        processing_seconds = time.time() - t0

        save_generation_run(
            original_filename=original_filename or "unknown",
            sport=sport,
            duration_seconds=result["duration"],
            windows=result["windows"],
            output_path=output_filename,
            processing_seconds=processing_seconds,
        )

        return jsonify(
            {
                "success": True,
                "output_url": f"/api/outputs/{output_filename}",
                "sport": sport,
                "duration": result["duration"],
                "num_highlights": len(result["windows"]),
                "processing_seconds": round(processing_seconds, 1),
                "windows": [
                    {"start": w[0], "end": w[1], "score": w[2]} for w in result["windows"]
                ],
            }
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/outputs/<path:filename>")
def serve_output(filename: str):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    print("SportsLab gateway running at http://localhost:8080")
    print("Open that URL in your browser — UI and AI backend are wired.")
    app.run(debug=True, host="0.0.0.0", port=8080, use_reloader=False)
