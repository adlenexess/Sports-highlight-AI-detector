"""
create_tables.py

This file creates all tables required for the
AI-Based Sports Highlight Generation System.
"""

import sqlite3
from database import create_connection


def create_tables():
    """
    Create all database tables.
    """

    connection = create_connection()

    if connection is None:
        print("Unable to connect to database.")
        return

    cursor = connection.cursor()

    try:

        cursor.execute("PRAGMA foreign_keys = ON")

        # -----------------------------
        # Table 1 : Sports
        # -----------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sports(
            sport_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_name TEXT NOT NULL UNIQUE
        )
        """)

        # -----------------------------
        # Table 2 : Matches
        # -----------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Matches(
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_id INTEGER NOT NULL,
            match_name TEXT NOT NULL,
            team_one TEXT NOT NULL,
            team_two TEXT NOT NULL,
            venue TEXT,
            match_date TEXT,

            FOREIGN KEY(sport_id)
            REFERENCES Sports(sport_id)
            ON DELETE CASCADE
        )
        """)

        # -----------------------------
        # Table 3 : Highlight Events
        # -----------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Highlight_Events(
            highlight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            crowd_emotion TEXT,
            confidence_score REAL,
            timestamp TEXT,
            video_path TEXT,
            audio_path TEXT,
            created_at TEXT,

            FOREIGN KEY(match_id)
            REFERENCES Matches(match_id)
            ON DELETE CASCADE
        )
        """)

        # -----------------------------
        # Table 4 : Crowd Emotion
        # -----------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Crowd_Emotion(
            emotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            highlight_id INTEGER NOT NULL,
            emotion TEXT,
            emotion_score REAL,

            FOREIGN KEY(highlight_id)
            REFERENCES Highlight_Events(highlight_id)
            ON DELETE CASCADE
        )
        """)

        # -----------------------------
        # Table 5 : Detection History
        # -----------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Detection_History(
            detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            highlight_id INTEGER NOT NULL,
            predicted_event TEXT,
            confidence REAL,
            model_version TEXT,
            detection_time TEXT,

            FOREIGN KEY(highlight_id)
            REFERENCES Highlight_Events(highlight_id)
            ON DELETE CASCADE
        )
        """)

        # -----------------------------
        # Table 6 : Processing Runs (gateway log)
        # -----------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Processing_Runs(
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            original_filename TEXT NOT NULL,
            sport_id INTEGER NOT NULL,
            output_path TEXT,
            duration_seconds REAL,
            num_highlights INTEGER,
            processing_seconds REAL,
            created_at TEXT NOT NULL,

            FOREIGN KEY(match_id)
            REFERENCES Matches(match_id)
            ON DELETE SET NULL,
            FOREIGN KEY(sport_id)
            REFERENCES Sports(sport_id)
        )
        """)

        connection.commit()

        print("All tables created successfully!")

    except sqlite3.Error as error:
        print("Database Error :", error)

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()
