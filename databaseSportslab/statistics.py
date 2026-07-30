"""
statistics.py

This file generates reports and statistics
from the SQLite database.
"""

import sqlite3
from database import create_connection


# -----------------------------------
# Total Sports
# -----------------------------------
def total_sports():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM Sports")

        total = cursor.fetchone()[0]

        print("Total Sports :", total)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Total Matches
# -----------------------------------
def total_matches():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM Matches")

        total = cursor.fetchone()[0]

        print("Total Matches :", total)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Total Highlights
# -----------------------------------
def total_highlights():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM Highlight_Events")

        total = cursor.fetchone()[0]

        print("Total Highlights :", total)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Total Sixes
# -----------------------------------
def total_sixes():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM Highlight_Events
        WHERE event_name='Six'
        """)

        total = cursor.fetchone()[0]

        print("Total Sixes :", total)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Total Goals
# -----------------------------------
def total_goals():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM Highlight_Events
        WHERE event_name='Goal'
        """)

        total = cursor.fetchone()[0]

        print("Total Goals :", total)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Total Wickets
# -----------------------------------
def total_wickets():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM Highlight_Events
        WHERE event_name='Wicket'
        """)

        total = cursor.fetchone()[0]

        print("Total Wickets :", total)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Average Confidence Score
# -----------------------------------
def average_confidence():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        SELECT AVG(confidence_score)
        FROM Highlight_Events
        """)

        average = cursor.fetchone()[0]

        if average is None:
            print("Average Confidence : N/A (no highlights yet)")
        else:
            print("Average Confidence :", round(average, 2))

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Emotion Statistics
# -----------------------------------
def emotion_statistics():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        SELECT emotion,
               COUNT(*)
        FROM Crowd_Emotion
        GROUP BY emotion
        """)

        records = cursor.fetchall()

        print("\nCrowd Emotion Statistics")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Match-wise Highlights
# -----------------------------------
def match_statistics():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        SELECT Matches.match_name,
               COUNT(Highlight_Events.highlight_id)

        FROM Matches

        JOIN Highlight_Events

        ON Matches.match_id =
        Highlight_Events.match_id

        GROUP BY Matches.match_name
        """)

        records = cursor.fetchall()

        print("\nMatch Statistics")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Main Program
# -----------------------------------
if __name__ == "__main__":

    total_sports()

    total_matches()

    total_highlights()

    total_sixes()

    total_goals()

    total_wickets()

    average_confidence()

    emotion_statistics()

    match_statistics()