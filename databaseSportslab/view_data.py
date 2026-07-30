"""
view_data.py

This file displays data stored in the SQLite database.
"""

import sqlite3
from database import create_connection


# -----------------------------
# View Sports
# -----------------------------
def view_sports():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = "SELECT * FROM Sports"

        cursor.execute(query)

        records = cursor.fetchall()

        print("\n------ Sports ------")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------
# View Matches
# -----------------------------
def view_matches():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = "SELECT * FROM Matches"

        cursor.execute(query)

        records = cursor.fetchall()

        print("\n------ Matches ------")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# View Highlight Events
# -----------------------------
def view_highlights():

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = "SELECT * FROM Highlight_Events"

        cursor.execute(query)

        records = cursor.fetchall()

        print("\n------ Highlight Events ------")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# View Crowd Emotion
# -----------------------------
def view_emotions():

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = "SELECT * FROM Crowd_Emotion"

        cursor.execute(query)

        records = cursor.fetchall()

        print("\n------ Crowd Emotion ------")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# View Detection History
# -----------------------------
def view_detection_history():

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = "SELECT * FROM Detection_History"

        cursor.execute(query)

        records = cursor.fetchall()

        print("\n------ Detection History ------")

        for row in records:
            print(row)

    except sqlite3.Error as error:
        print(error)

    finally:
        connection.close()


# -----------------------------
# Main Function
# -----------------------------
if __name__ == "__main__":

    view_sports()

    view_matches()

    view_highlights()

    view_emotions()

    view_detection_history()