"""
SportsLab integration gateway.

Serves the SportsLab UI unchanged from disk, injects integration/wire.js at
serve time, and exposes a JSON API that calls the AI highlight detector
backend services directly. Completed runs are logged to SQLite
(databaseSportslab).

Run from the SportsLab project root:
    python integration/gateway.py

SECURITY (Optional, backward compatible):
    Create a .env file to enable optional security features:
    - API_KEY: Require X-API-Key header for API requests
    - RATE_LIMIT_PER_MINUTE: Limit requests per minute per IP
    - API_REQUEST_LOGGING: Log all API requests
    
    If no .env file exists, the API works normally (open access).
"""

from __future__ import annotations

import os
import sys
import time
import uuid
import mimetypes
import tempfile
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta

import imageio_ffmpeg
from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename

# Load environment variables from .env if it exists (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, that's okay - we'll just use defaults
    pass

# ---------------------------------------------------------------------------
# Optional Configuration from environment variables
# (All optional - API works without .env file)
# ---------------------------------------------------------------------------
API_KEY = os.getenv("API_KEY", "").strip() or None
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "0")) or None
API_REQUEST_LOGGING = os.getenv("API_REQUEST_LOGGING", "False").lower() == "true"
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500"))
MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Request tracking for rate limiting
_request_log = defaultdict(list)
_api_log_file = None

if API_REQUEST_LOGGING:
    _api_log_file = os.path.join(
        os.path.dirname(__file__),
        "api_requests.log"
    )

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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

init_db()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

WIRE_SCRIPT_TAG = '<script src="/integration/wire.js"></script>'
INJECT_BEFORE = '<script src="js/app.js"></script>'


# ---------------------------------------------------------------------------
# Optional Security Features
# ---------------------------------------------------------------------------
def log_api_request(endpoint, ip, success, error=None):
    """Log API request to file if enabled."""
    if not API_REQUEST_LOGGING or not _api_log_file:
        return
    
    try:
        with open(_api_log_file, "a") as f:
            timestamp = datetime.now().isoformat()
            status = "SUCCESS" if success else f"FAILED: {error}"
            f.write(f"{timestamp} | IP: {ip} | Endpoint: {endpoint} | {status}\n")
    except Exception as e:
        print(f"Warning: could not write to API log: {e}")


def check_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded rate limit (if enabled)."""
    if not RATE_LIMIT_PER_MINUTE:
        return True  # Rate limiting disabled
    
    now = datetime.now()
    cutoff = now - timedelta(minutes=1)
    
    # Clean old entries
    _request_log[ip] = [
        ts for ts in _request_log[ip] if ts > cutoff
    ]
    
    if len(_request_log[ip]) >= RATE_LIMIT_PER_MINUTE:
        return False  # Rate limit exceeded
    
    _request_log[ip].append(now)
    return True  # Request allowed


def require_api_key(f):
    """Decorator to require API key if configured."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not API_KEY:
            # No API key configured, allow request
            return f(*args, **kwargs)
        
        # API key is required - check header or form parameter
        provided_key = (
            request.headers.get("X-API-Key") or
            request.form.get("api_key")
        )
        
        if not provided_key or provided_key != API_KEY:
            log_api_request("/api/generate", request.remote_addr, False, "Unauthorized")
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def check_api_rate_limit(f):
    """Decorator to enforce rate limiting if configured."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_rate_limit(request.remote_addr):
            log_api_request(
                "/api/generate",
                request.remote_addr,
                False,
                "Rate limit exceeded"
            )
            return jsonify({
                "success": False,
                "error": f"Rate limit exceeded. Max {RATE_LIMIT_PER_MINUTE} requests per minute."
            }), 429
        
        return f(*args, **kwargs)
    
    return decorated_function


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


# Main API endpoint - same as before, but with optional security
@app.route("/api/generate", methods=["POST"])
@check_api_rate_limit
@require_api_key
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
                log_api_request("/api/generate", request.remote_addr, False, "No URL provided")
                return jsonify({"success": False, "error": "Please paste a video URL."}), 400
            saved_path = downloader.fetch_video_from_url(video_url, UPLOAD_FOLDER)
            original_filename = os.path.basename(saved_path)
        else:
            if "video" not in request.files:
                log_api_request("/api/generate", request.remote_addr, False, "No file provided")
                return jsonify({"success": False, "error": "No video file provided."}), 400

            file = request.files["video"]
            if not file or file.filename == "":
                log_api_request("/api/generate", request.remote_addr, False, "Empty file")
                return jsonify({"success": False, "error": "No file selected."}), 400
            if not allowed_file(file.filename):
                log_api_request("/api/generate", request.remote_addr, False, "Invalid file type")
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

        response_data = {
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
        
        log_api_request("/api/generate", request.remote_addr, True)
        return jsonify(response_data)
        
    except Exception as exc:
        import traceback
        traceback.print_exc()
        log_api_request("/api/generate", request.remote_addr, False, str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/outputs/<path:filename>")
def serve_output(filename: str):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    print("=" * 70)
    print("SportsLab gateway running at http://localhost:8080")
    print("=" * 70)
    print("Open that URL in your browser — UI and AI backend are wired.")
    print()
    
    # Show security status
    if API_KEY:
        print("🔒 API authentication ENABLED")
        print(f"   Clients must include: X-API-Key: {API_KEY[:8]}...")
    else:
        print("ℹ️  API authentication disabled (set API_KEY in .env to enable)")
    
    if RATE_LIMIT_PER_MINUTE:
        print(f"⏱️  Rate limiting ENABLED: {RATE_LIMIT_PER_MINUTE} requests/minute per IP")
    else:
        print("ℹ️  Rate limiting disabled (set RATE_LIMIT_PER_MINUTE in .env to enable)")
    
    if API_REQUEST_LOGGING:
        print(f"📝 Request logging ENABLED: {_api_log_file}")
    else:
        print("ℹ️  Request logging disabled (set API_REQUEST_LOGGING=True in .env to enable)")
    
    print()
    print("💡 To enable security features, create .env file in project root")
    print("   See .env.example for configuration options")
    print("=" * 70)
    print()
    
    app.run(debug=False, host="0.0.0.0", port=8080, use_reloader=False)
