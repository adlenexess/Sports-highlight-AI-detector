"""
delete_data.py

This file deletes records from the SQLite database.
"""

import sqlite3
from database import create_connection


# -----------------------------------
# Delete Sport
# -----------------------------------
def delete_sport(sport_id):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        DELETE FROM Sports
        WHERE sport_id = ?
        """

        cursor.execute(query, (sport_id,))

        connection.commit()

        if cursor.rowcount > 0:
            print("Sport deleted successfully.")
        else:
            print("Sport ID not found.")

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------------
# Delete Match
# -----------------------------------
def delete_match(match_id):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        DELETE FROM Matches
        WHERE match_id = ?
        """

        cursor.execute(query, (match_id,))

        connection.commit()

        if cursor.rowcount > 0:
            print("Match deleted successfully.")
        else:
            print("Match ID not found.")

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------------
# Delete Highlight
# -----------------------------------
def delete_highlight(highlight_id):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        DELETE FROM Highlight_Events
        WHERE highlight_id = ?
        """

        cursor.execute(query, (highlight_id,))

        connection.commit()

        if cursor.rowcount > 0:
            print("Highlight deleted successfully.")
        else:
            print("Highlight ID not found.")

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------------
# Delete Emotion
# -----------------------------------
def delete_emotion(highlight_id):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        DELETE FROM Crowd_Emotion
        WHERE highlight_id = ?
        """

        cursor.execute(query, (highlight_id,))

        connection.commit()

        if cursor.rowcount > 0:
            print("Emotion deleted successfully.")
        else:
            print("Highlight ID not found.")

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------------
# Delete Detection History
# -----------------------------------
def delete_detection(highlight_id):

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        DELETE FROM Detection_History
        WHERE highlight_id = ?
        """

        cursor.execute(query, (highlight_id,))

        connection.commit()

        if cursor.rowcount > 0:
            print("Detection history deleted successfully.")
        else:
            print("Highlight ID not found.")

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------------
# Delete All Highlights
# -----------------------------------
def delete_all_highlights():

    connection = create_connection()

    try:
        cursor = connection.cursor()

        query = """
        DELETE FROM Highlight_Events
        """

        cursor.execute(query)

        connection.commit()

        print("All highlights deleted successfully.")

    except sqlite3.Error as error:
        print("Error :", error)

    finally:
        connection.close()


# -----------------------------------
# Test Program
# -----------------------------------
if __name__ == "__main__":

    # Delete Highlight with ID = 1
    delete_highlight(1)

    # Delete Match with ID = 1
    delete_match(1)

    # Delete Sport with ID = 2
    delete_sport(2)

    # Delete Emotion of Highlight ID = 1
    delete_emotion(1)

    # Delete Detection History of Highlight ID = 1
    delete_detection(1)

    # Uncomment the line below to delete all highlights
    # delete_all_highlights()