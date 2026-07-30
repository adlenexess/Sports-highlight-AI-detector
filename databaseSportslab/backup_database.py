"""
backup_database.py

This file is used to create and restore
SQLite database backups.
"""

import shutil
import os

from database import DB_PATH


DATABASE_NAME = DB_PATH
BACKUP_NAME = os.path.join(os.path.dirname(DB_PATH), "sports_highlight_backup.db")


# -------------------------------------
# Create Database Backup
# -------------------------------------
def backup_database():

    try:

        if os.path.exists(DATABASE_NAME):

            shutil.copy(DATABASE_NAME, BACKUP_NAME)

            print("Database backup created successfully!")

        else:

            print("Database file not found.")

    except Exception as error:

        print("Error :", error)


# -------------------------------------
# Restore Database
# -------------------------------------
def restore_database():

    try:

        if os.path.exists(BACKUP_NAME):

            shutil.copy(BACKUP_NAME, DATABASE_NAME)

            print("Database restored successfully!")

        else:

            print("Backup file not found.")

    except Exception as error:

        print("Error :", error)


# -------------------------------------
# Show Database Information
# -------------------------------------
def database_info():

    if os.path.exists(DATABASE_NAME):

        size = os.path.getsize(DATABASE_NAME)

        print("Database Name :", DATABASE_NAME)

        print("Database Size :", size, "bytes")

    else:

        print("Database not found.")


# -------------------------------------
# Delete Backup File
# -------------------------------------
def delete_backup():

    try:

        if os.path.exists(BACKUP_NAME):

            os.remove(BACKUP_NAME)

            print("Backup deleted successfully.")

        else:

            print("Backup file does not exist.")

    except Exception as error:

        print(error)


# -------------------------------------
# Main Program
# -------------------------------------
if __name__ == "__main__":

    print("------ Database Backup Utility ------")

    database_info()

    backup_database()

    # Uncomment to restore database
    # restore_database()

    # Uncomment to delete backup
    # delete_backup()