"""
database.py

This file is responsible for connecting Python with the SQLite3 database.
"""

import os
import sqlite3

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "sports_highlight.db")


def create_connection(verbose=False):
    """
    Create and return a database connection.
    """

    try:
        connection = sqlite3.connect(DB_PATH)
        connection.execute("PRAGMA foreign_keys = ON")

        if verbose:
            print("Database Connected Successfully!")

        return connection

    except sqlite3.Error as error:
        print("Database Error:", error)

        return None


def close_connection(connection):
    """
    Close database connection.
    """

    try:
        if connection:
            connection.close()
            print("Database Connection Closed.")

    except sqlite3.Error as error:
        print("Error:", error)


# Test the connection
if __name__ == "__main__":

    conn = create_connection(verbose=True)

    close_connection(conn)