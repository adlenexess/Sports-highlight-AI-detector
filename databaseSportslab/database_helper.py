"""
database_helper.py

Common reusable database helper functions.
"""

import sqlite3
from database import create_connection


# -------------------------------------
# Execute INSERT, UPDATE, DELETE Queries
# -------------------------------------
def execute_query(query, values=()):
    """
    Execute INSERT, UPDATE, DELETE queries.
    """

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(query, values)

        connection.commit()

        print("Query executed successfully.")

    except sqlite3.Error as error:
        print("Database Error:", error)

    finally:
        connection.close()


# -------------------------------------
# Fetch All Records
# -------------------------------------
def fetch_all(query, values=()):
    """
    Return all records.
    """

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(query, values)

        return cursor.fetchall()

    except sqlite3.Error as error:
        print("Database Error:", error)
        return []

    finally:
        connection.close()


# -------------------------------------
# Fetch One Record
# -------------------------------------
def fetch_one(query, values=()):
    """
    Return a single record.
    """

    connection = create_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(query, values)

        return cursor.fetchone()

    except sqlite3.Error as error:
        print("Database Error:", error)
        return None

    finally:
        connection.close()


# -------------------------------------
# Check Record Exists
# -------------------------------------
def record_exists(table_name, column_name, value):
    """
    Check whether a record exists.
    """

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = f"""
        SELECT COUNT(*)
        FROM {table_name}
        WHERE {column_name}=?
        """

        cursor.execute(query, (value,))

        count = cursor.fetchone()[0]

        return count > 0

    except sqlite3.Error as error:
        print("Database Error:", error)
        return False

    finally:
        connection.close()


# -------------------------------------
# Total Records
# -------------------------------------
def total_records(table_name):
    """
    Count total records in a table.
    """

    connection = create_connection()

    try:

        cursor = connection.cursor()

        query = f"""
        SELECT COUNT(*)
        FROM {table_name}
        """

        cursor.execute(query)

        return cursor.fetchone()[0]

    except sqlite3.Error as error:
        print(error)
        return 0

    finally:
        connection.close()


# -------------------------------------
# Test Program
# -------------------------------------
if __name__ == "__main__":

    print("Total Sports :", total_records("Sports"))

    print("Sport Exists :",
          record_exists("Sports",
                        "sport_name",
                        "Cricket"))

    sports = fetch_all("SELECT * FROM Sports")

    print("\nSports Table")

    for sport in sports:
        print(sport)