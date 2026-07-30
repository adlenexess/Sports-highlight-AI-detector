"""
persistence.py

SQLite persistence bridge used by integration/gateway.py.
Maps AI highlight windows into the normalized SportsLab schema.
"""

from __future__ import annotations

from datetime import datetime

from create_tables import create_tables
from database import create_connection

DEFAULT_SPORTS = ("Cricket", "Football")
MODEL_VERSION = "AI_Model_v1"


def _format_timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _emotion_from_score(score: float) -> tuple[str, float]:
    pct = score * 100
    if pct >= 75:
        return "Excited", pct
    if pct >= 50:
        return "Engaged", pct
    return "Neutral", pct


def init_db() -> None:
    """Create tables and seed default sports for the UI picker."""
    create_tables()
    _seed_default_sports()


def _seed_default_sports() -> None:
    connection = create_connection()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        for sport_name in DEFAULT_SPORTS:
            cursor.execute(
                "INSERT OR IGNORE INTO Sports(sport_name) VALUES(?)",
                (sport_name,),
            )
        connection.commit()
    finally:
        connection.close()


def _get_or_create_sport_id(connection, sport: str) -> int:
    sport_label = sport.strip().capitalize()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT sport_id FROM Sports WHERE lower(sport_name) = lower(?)",
        (sport_label,),
    )
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("INSERT INTO Sports(sport_name) VALUES(?)", (sport_label,))
    return cursor.lastrowid


def save_generation_run(
    original_filename: str,
    sport: str,
    duration_seconds: float,
    windows: list,
    output_path: str,
    processing_seconds: float,
) -> int | None:
    """
    Persist one completed highlight generation run.
    Returns run_id on success, None on failure (never raises).
    """
    connection = create_connection()
    if connection is None:
        return None

    try:
        cursor = connection.cursor()
        sport_id = _get_or_create_sport_id(connection, sport)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.now().strftime("%Y-%m-%d")
        match_name = f"{original_filename} ({today})"

        cursor.execute(
            """
            INSERT INTO Matches
            (sport_id, match_name, team_one, team_two, venue, match_date)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (sport_id, match_name, "—", "—", None, today),
        )
        match_id = cursor.lastrowid

        for index, window in enumerate(windows):
            start, end, score = window[0], window[1], window[2]
            timestamp = f"{_format_timestamp(start)}–{_format_timestamp(end)}"
            emotion, emotion_score = _emotion_from_score(score)
            confidence = round(score * 100, 2)

            cursor.execute(
                """
                INSERT INTO Highlight_Events
                (match_id, event_name, crowd_emotion, confidence_score,
                 timestamp, video_path, audio_path, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    match_id,
                    "Highlight",
                    emotion,
                    confidence,
                    timestamp,
                    output_path if index == 0 else None,
                    None,
                    now,
                ),
            )
            highlight_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO Crowd_Emotion (highlight_id, emotion, emotion_score)
                VALUES(?, ?, ?)
                """,
                (highlight_id, emotion, round(emotion_score, 2)),
            )
            cursor.execute(
                """
                INSERT INTO Detection_History
                (highlight_id, predicted_event, confidence, model_version, detection_time)
                VALUES(?, ?, ?, ?, ?)
                """,
                (highlight_id, "Highlight", confidence, MODEL_VERSION, now),
            )

        cursor.execute(
            """
            INSERT INTO Processing_Runs
            (match_id, original_filename, sport_id, output_path,
             duration_seconds, num_highlights, processing_seconds, created_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id,
                original_filename,
                sport_id,
                output_path,
                duration_seconds,
                len(windows),
                processing_seconds,
                now,
            ),
        )
        run_id = cursor.lastrowid
        connection.commit()
        return run_id

    except Exception as error:
        print(f"[persistence] WARNING: could not save run ({error})")
        return None

    finally:
        connection.close()


def get_recent_runs(limit: int = 20) -> list[dict]:
    """Return recent processing runs for optional admin/history views."""
    connection = create_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                r.run_id,
                r.original_filename,
                s.sport_name,
                r.duration_seconds,
                r.num_highlights,
                r.output_path,
                r.processing_seconds,
                r.created_at
            FROM Processing_Runs r
            JOIN Sports s ON r.sport_id = s.sport_id
            ORDER BY r.run_id DESC
            LIMIT ?
            """,
            (limit,),
        )
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as error:
        print(f"[persistence] WARNING: could not fetch history ({error})")
        return []
    finally:
        connection.close()
