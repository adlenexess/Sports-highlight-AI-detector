# SportsLab — AI Sports Highlight Generator

An AI-based system that transforms full-length sports match videos into concise highlight reels. SportsLab combines computer vision, audio analysis, and scene detection to identify exciting moments, stitches them into a downloadable video, and logs every run to a SQLite database.

Supported sports in the UI: **Cricket** and **Football**. The detection backend also accepts basketball, tennis, and generic sport profiles.

---

## Features

- **Multi-signal detection** — Motion, scene cuts, audio spikes, and replay cues are analyzed in parallel and fused into highlight windows.
- **Web UI** — Upload a video file or paste a URL, pick a sport, and download the generated highlight reel.
- **SQLite persistence** — Each generation run is stored with match metadata, highlight events, crowd emotion scores, and detection history.
- **CLI database manager** — Interactive menu for manual CRUD, search, statistics, and backup/restore.
- **Integration gateway** — A single Flask server serves the UI, wires it to the AI backend, and exposes a JSON API.

---

## Project Structure

```
database/
├── index.html              # SportsLab landing / upload / result UI
├── css/                    # Styles
├── js/app.js               # Frontend logic (sport picker, navigation)
├── assets/                 # Logos and sport icons
│
├── integration/
│   ├── gateway.py          # Main entry point — UI + API + AI pipeline
│   ├── wire.js             # Bridges UI buttons to /api/generate
│   ├── start.ps1           # Windows startup script (installs deps if needed)
│   └── start.bat           # Wrapper for start.ps1
│
├── backend/
│   └── algorithm/
│       └── AI-Powered-highlight-detector-main/
│       ├── app.py          # Standalone Flask app (optional; uses MySQL)
│       ├── requirements.txt
│       └── services/
│           ├── highlight_detector.py   # Orchestrates the full pipeline
│           ├── motion_detector.py
│           ├── scene_detector.py
│           ├── audio_detector.py
│           ├── replay_detector.py
│           ├── fusion.py
│           ├── clip_generator.py
│           └── downloader.py
│
└── databaseSportslab/
    ├── main.py             # CLI menu for database operations
    ├── database.py         # SQLite connection (sports_highlight.db)
    ├── create_tables.py    # Schema creation
    ├── persistence.py      # Gateway → database bridge
    ├── insert_data.py      # Insert sports, matches, highlights
    ├── view_data.py        # View table contents
    ├── search_data.py      # Search by sport
    ├── update_data.py      # Update highlights
    ├── delete_data.py      # Delete highlights
    ├── statistics.py       # Reports and aggregates
    └── backup_database.py  # Backup and restore
```

---

## Requirements

- **Python 3.11+** (3.13 tested)
- **FFmpeg** — Bundled via `imageio-ffmpeg` at runtime; no separate install required for most setups.
- **Windows** — `start.ps1` / `start.bat` are provided; on macOS/Linux, run `gateway.py` directly (see below).

### Python dependencies

Listed in `backend/algorithm/AI-Powered-highlight-detector-main/requirements.txt`:

| Package | Purpose |
|---------|---------|
| Flask | Web server and API |
| opencv-python | Motion / video analysis |
| moviepy | Video clip assembly |
| librosa, soundfile | Audio spike detection |
| scenedetect | Scene cut detection |
| numpy | Signal processing |
| yt-dlp, requests | Video download from URLs |
| mysql-connector-python | Only for standalone `app.py` (MySQL mode) |

---

## Quick Start

### Option 1 — Integration gateway (recommended)

This runs the full SportsLab UI wired to the AI backend and SQLite database.

**Windows:**

```powershell
.\integration\start.bat
```

Or:

```powershell
.\integration\start.ps1
```

The script uses `backend\algorithm\.venv` if present, otherwise system Python (`py -3`), and installs dependencies on first run.

Open **http://localhost:8080** in your browser.

**macOS / Linux:**

```bash
cd databaseSportslab   # or project root — gateway adds paths automatically
pip install -r "../backend/algorithm/AI-Powered-highlight-detector-main/requirements.txt"
python ../integration/gateway.py
```

### Option 2 — CLI database manager

For manual database operations without the web UI:

```bash
cd databaseSportslab
python main.py
```

Menu options include creating tables, inserting/viewing data, search, statistics, backup, and restore.

### Option 3 — Standalone AI detector app

The backend can run independently with its own Flask templates (uses **MySQL**, not SQLite):

```bash
cd backend/algorithm/AI-Powered-highlight-detector-main
pip install -r requirements.txt
python app.py
```

Configure MySQL connection in `services/db.py` before use.

---

## How It Works

1. **Upload** — User selects cricket or football and provides a video file or URL.
2. **Detection** — `highlight_detector.py` runs motion, scene, and audio detectors in parallel, then replay detection and signal fusion.
3. **Clip generation** — `clip_generator.py` extracts highlight windows and assembles `highlight_<id>.mp4`.
4. **Persistence** — `persistence.py` writes the run to SQLite: match row, highlight events, crowd emotion, detection history, and a `Processing_Runs` log entry.
5. **Download** — The UI receives the output URL and enables download via `wire.js`.

```
┌─────────────┐     wire.js      ┌──────────────┐     analyze_video     ┌─────────────────┐
│  SportsLab  │ ───────────────► │  gateway.py  │ ────────────────────► │ AI detector     │
│  (browser)  │   /api/generate  │  Flask :8080 │                       │ services/       │
└─────────────┘                  └──────┬───────┘                       └─────────────────┘
                                        │
                                        │ save_generation_run()
                                        ▼
                               ┌─────────────────┐
                               │ sports_highlight│
                               │ .db (SQLite)    │
                               └─────────────────┘
```

---

## Database Schema

SQLite file: `databaseSportslab/sports_highlight.db`

| Table | Description |
|-------|-------------|
| `Sports` | Sport types (Cricket, Football, …) |
| `Matches` | Match metadata linked to a sport |
| `Highlight_Events` | Detected highlights with confidence, timestamp, paths |
| `Crowd_Emotion` | Emotion labels and scores per highlight |
| `Detection_History` | Model predictions and versions per highlight |
| `Processing_Runs` | Gateway log: filename, sport, duration, output path, timing |

Foreign keys use `ON DELETE CASCADE` (or `SET NULL` for `Processing_Runs.match_id`).

---

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Server port | `integration/gateway.py` | `8080` |
| Upload folder | `backend/algorithm/.../static/uploads` | Auto-created |
| Output folder | `backend/algorithm/.../static/outputs` | Auto-created |
| Database path | `databaseSportslab/database.py` | `sports_highlight.db` |
| Highlight threshold | `highlight_detector.py` | `0.45` |
| Max highlights | `highlight_detector.py` | `8` |

---

## Troubleshooting

- **Dependencies missing** — Run `pip install -r "backend/algorithm/AI-Powered-highlight-detector-main/requirements.txt"`.
- **Port in use** — Change `port=8080` in `gateway.py` or stop the conflicting process.
- **Video processing fails** — Confirm the file is a supported format and under 500 MB; check terminal output for FFmpeg errors.
- **Database errors** — Run option 1 (Create Tables) in `databaseSportslab/main.py`, or call `create_tables()` from `create_tables.py`.
- **UI works but highlights are mock** — Ensure you opened the app via the gateway (`localhost:8080`), not by opening `index.html` directly; `wire.js` must be injected by the server.

---

## License

See individual component repositories for license terms. The AI highlight detector backend is based on the AI-Powered-highlight-detector project.
