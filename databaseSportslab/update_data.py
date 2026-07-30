"""
update_data.py

This file updates records in the SQLite database.
"""

import sqlite3
from database import create_connection


# -----------------------------------
# Update Sport Name
# -----------------------------------
def update_sport(sport_id, new_sport_name):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE Sports
        SET sport_name = ?
        WHERE sport_id = ?
        """

        cursor.execute(query, (new_sport_name, sport_id))

        connection.commit()

        if cursor.rowcount > 0:
            print("Sport updated successfully.")
        else:
            print("Sport ID not found.")

    except sqlite3.Error as error:
        print("Error:", error)

    finally:
        connection.close()


# -----------------------------------
# Update Match Details
# -----------------------------------
def update_match(match_id, venue, match_date):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE Matches
        SET venue = ?, match_date = ?
        WHERE match_id = ?
        """

        cursor.execute(query, (venue, match_date, match_id))

        connection.commit()

        if cursor.rowcount > 0:
            print("Match updated successfully.")
        else:
            print("Match ID not found.")

    except sqlite3.Error as error:
        print("Error:", error)

    finally:
        connection.close()


# -----------------------------------
# Update Highlight Event
# -----------------------------------
def update_highlight(highlight_id,
                     event_name,
                     crowd_emotion,
                     confidence_score):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE Highlight_Events
        SET event_name = ?,
            crowd_emotion = ?,
            confidence_score = ?
        WHERE highlight_id = ?
        """

        cursor.execute(query,
                       (event_name,
                        crowd_emotion,
                        confidence_score,
                        highlight_id))

        connection.commit()

        if cursor.rowcount > 0:
            print("Highlight updated successfully.")
        else:
            print("Highlight ID not found.")

    except sqlite3.Error as error:
        print("Error:", error)

    finally:
        connection.close()


# -----------------------------------
# Update Crowd Emotion
# -----------------------------------
def update_emotion(highlight_id,
                   emotion,
                   emotion_score):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE Crowd_Emotion
        SET emotion = ?,
            emotion_score = ?
        WHERE highlight_id = ?
        """

        cursor.execute(query,
                       (emotion,
                        emotion_score,
                        highlight_id))

        connection.commit()

        if cursor.rowcount > 0:
            print("Emotion updated successfully.")
        else:
            print("Highlight ID not found.")

    except sqlite3.Error as error:
        print("Error:", error)

    finally:
        connection.close()


# -----------------------------------
# Update Detection History
# -----------------------------------
def update_detection(highlight_id,
                     predicted_event,
                     confidence,
                     model_version):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        UPDATE Detection_History
        SET predicted_event = ?,
            confidence = ?,
            model_version = ?
        WHERE highlight_id = ?
        """

        cursor.execute(query,
                       (predicted_event,
                        confidence,
                        model_version,
                        highlight_id))

        connection.commit()

        if cursor.rowcount > 0:
            print("Detection history updated successfully.")
        else:
            print("Highlight ID not found.")

    except sqlite3.Error as error:
        print("Error:", error)

    finally:
        connection.close()


# -----------------------------------
# Test Program
# -----------------------------------
if __name__ == "__main__":

    update_sport(1, "Cricket")

    update_match(
        1,
        "Wankhede Stadium",
        "2026-08-01"
    )

    update_highlight(
        1,
        "Six",
        "Very Excited",
        99.80
    )

    update_emotion(
        1,
        "Cheering",
        98.60
    )

    update_detection(
        1,
        "Six",
        99.80,
        "AI_Model_v2"
    )