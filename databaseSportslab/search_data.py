"""
search_data.py

This file searches data from the SQLite database.
"""

import sqlite3
from database import create_connection


# -----------------------------------
# Search by Sport Name
# -----------------------------------
def search_by_sport(sport_name):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT h.highlight_id,
               s.sport_name,
               h.event_name,
               h.crowd_emotion,
               h.confidence_score
        FROM Highlight_Events h
        JOIN Matches m
            ON h.match_id = m.match_id
        JOIN Sports s
            ON m.sport_id = s.sport_id
        WHERE s.sport_name = ?
        """

        cursor.execute(query, (sport_name,))

        records = cursor.fetchall()

        print("\nSearch Result")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Search by Event Name
# -----------------------------------
def search_by_event(event_name):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT *
        FROM Highlight_Events
        WHERE event_name = ?
        """

        cursor.execute(query, (event_name,))

        records = cursor.fetchall()

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Search by Crowd Emotion
# -----------------------------------
def search_by_emotion(emotion):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT *
        FROM Crowd_Emotion
        WHERE emotion = ?
        """

        cursor.execute(query, (emotion,))

        records = cursor.fetchall()

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Search by Match Name
# -----------------------------------
def search_by_match(match_name):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT *
        FROM Matches
        WHERE match_name = ?
        """

        cursor.execute(query, (match_name,))

        records = cursor.fetchall()

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------------
# Search by Confidence Score
# -----------------------------------
def search_by_confidence(score):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        SELECT *
        FROM Highlight_Events
        WHERE confidence_score >= ?
        """

        cursor.execute(query, (score,))

        records = cursor.fetchall()

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

    print("Search by Sport")
    search_by_sport("Cricket")

    print("\nSearch by Event")
    search_by_event("Six")

    print("\nSearch by Emotion")
    search_by_emotion("Cheering")

    print("\nSearch by Match")
    search_by_match("India vs Australia")

    print("\nSearch by Confidence")
    search_by_confidence(90)