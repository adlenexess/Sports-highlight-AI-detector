"""
db.py
-----
Minimal MySQL logging layer. Every processed video gets one row: original
filename, chosen sport, duration, number of highlights found, output path,
and processing time. This satisfies the "MYSQL DBMS" component of the
project brief and gives you something real to show in a viva (query the
table live, show history of runs, etc.) without over-engineering a full
ORM for a college project.

SETUP:
    1. Install MySQL locally (or use XAMPP/WAMP's MySQL).
    2. Create the database:
           CREATE DATABASE highlight_db;
    3. Set these env vars (or edit the defaults below) before running app.py:
           MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
    4. Run this file once to create the table:
           python services/db.py
"""

import os
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DB", "highlight_db"),
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS processed_videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    sport VARCHAR(50) NOT NULL,
    duration_seconds FLOAT,
    num_highlights INT,
    output_path VARCHAR(255),
    processing_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create the table if it doesn't exist. Safe to call on every app start."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        cursor.close()
        conn.close()
        print("[db] Table ready.")
    except Error as e:
        print(f"[db] WARNING: could not connect to MySQL ({e}). "
              f"App will still work, but runs won't be logged.")


def log_run(original_filename, sport, duration_seconds, num_highlights,
            output_path, processing_seconds):
    """Insert one row for a completed run. Fails silently if MySQL is down
    so a DB outage never breaks the actual highlight generation feature."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO processed_videos
               (original_filename, sport, duration_seconds, num_highlights,
                output_path, processing_seconds)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (original_filename, sport, duration_seconds, num_highlights,
             output_path, processing_seconds),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[db] WARNING: could not log run ({e})")


def get_history(limit=20):
    """Return the most recent processed videos, for a history/dashboard view."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM processed_videos ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print(f"[db] WARNING: could not fetch history ({e})")
        return []


if __name__ == "__main__":
    init_db()
