"""
main.py

Main menu for AI-Based Sports Highlight Generation System.
"""

from create_tables import create_tables
from insert_data import (
    insert_sport,
    insert_match,
    insert_highlight
)
from view_data import (
    view_sports,
    view_matches,
    view_highlights
)
from search_data import search_by_sport
from update_data import update_highlight
from delete_data import delete_highlight
from statistics import (
    total_highlights,
    average_confidence
)
from backup_database import (
    backup_database,
    restore_database
)


def menu():

    while True:

        print("\n==============================")
        print(" AI Sports Highlight System ")
        print("==============================")
        print("1. Create Tables")
        print("2. Insert Sport")
        print("3. Insert Match")
        print("4. Insert Highlight")
        print("5. View Sports")
        print("6. View Matches")
        print("7. View Highlights")
        print("8. Search by Sport")
        print("9. Update Highlight")
        print("10. Delete Highlight")
        print("11. Show Statistics")
        print("12. Backup Database")
        print("13. Restore Database")
        print("14. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            create_tables()

        elif choice == "2":
            sport = input("Enter Sport Name: ")
            insert_sport(sport)

        elif choice == "3":
            sport_id = int(input("Sport ID: "))
            match_name = input("Match Name: ")
            team1 = input("Team One: ")
            team2 = input("Team Two: ")
            venue = input("Venue: ")
            date = input("Match Date: ")

            insert_match(
                sport_id,
                match_name,
                team1,
                team2,
                venue,
                date
            )

        elif choice == "4":

            match_id = int(input("Match ID: "))
            event = input("Event Name: ")
            emotion = input("Crowd Emotion: ")
            confidence = float(input("Confidence Score: "))
            timestamp = input("Timestamp: ")
            video = input("Video Path: ")
            audio = input("Audio Path: ")
            created = input("Created At: ")

            insert_highlight(
                match_id,
                event,
                emotion,
                confidence,
                timestamp,
                video,
                audio,
                created
            )

        elif choice == "5":
            view_sports()

        elif choice == "6":
            view_matches()

        elif choice == "7":
            view_highlights()

        elif choice == "8":

            sport = input("Enter Sport Name: ")
            search_by_sport(sport)

        elif choice == "9":

            hid = int(input("Highlight ID: "))
            event = input("New Event: ")
            emotion = input("New Emotion: ")
            score = float(input("New Confidence: "))

            update_highlight(
                hid,
                event,
                emotion,
                score
            )

        elif choice == "10":

            hid = int(input("Highlight ID: "))

            delete_highlight(hid)

        elif choice == "11":

            total_highlights()

            average_confidence()

        elif choice == "12":

            backup_database()

        elif choice == "13":

            restore_database()

        elif choice == "14":

            print("Thank You!")

            break

        else:

            print("Invalid Choice")


if __name__ == "__main__":
    menu()