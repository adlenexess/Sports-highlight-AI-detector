"""
app.py
------
Flask web application: user uploads a sports video, selects the sport,
we run the detection pipeline, generate highlight.mp4, log the run to
MySQL, and show the result with a download link.
"""

import os
import time
import uuid

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

from services.highlight_detector import analyze_video
from services.clip_generator import generate_highlight_video
from services import downloader
from services import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "static", "outputs")
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv"}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB upload cap

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

db.init_db()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    sport = request.form.get("sport", "generic")
    source_mode = request.form.get("source_mode", "file")  # "file" or "url"

    saved_path = None
    original_filename = None

    if source_mode == "url":
        video_url = request.form.get("video_url", "").strip()
        if not video_url:
            flash("Please paste a video URL.")
            return redirect(url_for("index"))

        try:
            saved_path = downloader.fetch_video_from_url(video_url, UPLOAD_FOLDER)
            original_filename = os.path.basename(saved_path)
        except Exception as e:
            flash(f"Could not download video from that URL: {e}")
            return redirect(url_for("index"))

    else:
        if "video" not in request.files:
            flash("No file part in the request.")
            return redirect(url_for("index"))

        file = request.files["video"]

        if file.filename == "":
            flash("No file selected.")
            return redirect(url_for("index"))

        if not allowed_file(file.filename):
            flash("Unsupported file type. Please upload mp4, mov, avi, or mkv.")
            return redirect(url_for("index"))

        original_filename = secure_filename(file.filename)
        unique_id = uuid.uuid4().hex[:8]
        saved_name = f"{unique_id}_{original_filename}"
        saved_path = os.path.join(UPLOAD_FOLDER, saved_name)
        file.save(saved_path)

    t0 = time.time()
    try:
        result = analyze_video(saved_path, sport=sport)
        output_filename = f"highlight_{unique_id}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        generate_highlight_video(saved_path, result["windows"], output_path)
    except Exception as e:
        flash(f"Processing failed: {e}")
        return redirect(url_for("index"))

    processing_seconds = time.time() - t0

    db.log_run(
        original_filename=original_filename,
        sport=sport,
        duration_seconds=result["duration"],
        num_highlights=len(result["windows"]),
        output_path=output_filename,
        processing_seconds=processing_seconds,
    )

    return render_template(
        "result.html",
        output_video=output_filename,
        windows=result["windows"],
        sport=sport,
        original_duration=result["duration"],
        processing_seconds=processing_seconds,
    )


@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route("/history")
def history():
    rows = db.get_history()
    return render_template("history.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
