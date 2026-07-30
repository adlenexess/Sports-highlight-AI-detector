"""
insert_data.py

This file inserts data into the SQLite database.
"""

import sqlite3
from database import create_connection


# -----------------------------
# Insert Sport
# -----------------------------
def insert_sport(sport_name):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO Sports(sport_name)
        VALUES(?)
        """

        cursor.execute(query, (sport_name,))

        connection.commit()

        print("Sport inserted successfully.")

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------
# Insert Match
# -----------------------------
def insert_match(sport_id, match_name,
                 team_one, team_two,
                 venue, match_date):

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO Matches
        (sport_id, match_name, team_one, team_two, venue, match_date)

        VALUES(?,?,?,?,?,?)
        """

        cursor.execute(query,
                       (sport_id,
                        match_name,
                        team_one,
                        team_two,
                        venue,
                        match_date))

        connection.commit()

        print("Match inserted successfully.")

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# Insert Highlight Event
# -----------------------------
def insert_highlight(match_id,
                     event_name,
                     crowd_emotion,
                     confidence_score,
                     timestamp,
                     video_path,
                     audio_path,
                     created_at):

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO Highlight_Events
        (match_id,event_name,crowd_emotion,
        confidence_score,timestamp,
        video_path,audio_path,created_at)

        VALUES(?,?,?,?,?,?,?,?)
        """

        cursor.execute(query,
                       (match_id,
                        event_name,
                        crowd_emotion,
                        confidence_score,
                        timestamp,
                        video_path,
                        audio_path,
                        created_at))

        connection.commit()

        print("Highlight inserted successfully.")

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# Insert Crowd Emotion
# -----------------------------
def insert_emotion(highlight_id,
                   emotion,
                   emotion_score):

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO Crowd_Emotion
        (highlight_id,emotion,emotion_score)

        VALUES(?,?,?)
        """

        cursor.execute(query,
                       (highlight_id,
                        emotion,
                        emotion_score))

        connection.commit()

        print("Emotion inserted successfully.")

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# Insert Detection History
# -----------------------------
def insert_detection(highlight_id,
                     predicted_event,
                     confidence,
                     model_version,
                     detection_time):

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO Detection_History
        (highlight_id,predicted_event,
        confidence,model_version,detection_time)

        VALUES(?,?,?,?,?)
        """

        cursor.execute(query,
                       (highlight_id,
                        predicted_event,
                        confidence,
                        model_version,
                        detection_time))

        connection.commit()

        print("Detection History inserted successfully.")

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# Test Program
# -----------------------------
if __name__ == "__main__":

    insert_sport("Cricket")
    insert_sport("Football")

    insert_match(
        1,
        "India vs Australia",
        "India",
        "Australia",
        "Ahmedabad",
        "2026-07-28"
    )

    insert_highlight(
        1,
        "Six",
        "Excited",
        98.5,
        "00:10:35",
        "videos/highlight1.mp4",
        "audio/highlight1.wav",
        "2026-07-28 10:30:00"
    )

    insert_emotion(
        1,
        "Cheering",
        97.8
    )

    insert_detection(
        1,
        "Six",
        98.5,
        "AI_Model_v1",
        "2026-07-28 10:30:05"
    )