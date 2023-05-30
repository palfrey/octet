import datetime
import os.path

from django.core.management.base import BaseCommand
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models import Contest, Event, Group, Organiser, Performance

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# https://docs.google.com/spreadsheets/d/1jIPkr5c_Zupl4Re0aoqjvoPpTTBrUbL0qXtD5BZOgms/edit?usp=sharing
SPREADSHEET_ID = "1jIPkr5c_Zupl4Re0aoqjvoPpTTBrUbL0qXtD5BZOgms"


class Command(BaseCommand):
    help = "Downloads sheet data"

    def handle(self, *args, **options):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("sheets", "v4", credentials=creds)
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range="A1:Q40")
                .execute()
            )
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return

            metadata = {}
            group = None
            organiser = None
            event = None
            contest = None
            index = None

            for row in values:
                if row == []:
                    continue
                if contest is None:
                    if row[0] != "":  # end of metadata
                        organiser = Organiser.objects.create(name=metadata["Who"])
                        date = datetime.datetime.strptime(
                            metadata["Contest date"], "%d/%m/%Y"
                        ).date()
                        event = Event.objects.create(
                            name=metadata["Event"],
                            organiser=organiser,
                            start_date=date,
                            end_date=date,
                        )
                        contest = Contest.objects.create(
                            event=event, name=metadata["Contest"]
                        )
                        continue
                    # getting metadata
                    key = row[1]
                    value = row[2]
                    metadata[key] = value
                    continue

                if row[0] != "":  # number for new entry
                    group = Group.objects.create(
                        name=row[1], director=row[2], member_count=int(row[3])
                    )
                    index = 1
                song_name = row[4]
                if song_name == "":
                    continue
                Performance.objects.create(
                    group=group,
                    contest=contest,
                    song_name=song_name,
                    music_score=int(row[6]),
                    performance_score=int(row[8]),
                    singing_score=int(row[10]),
                    index=index,
                )
                index += 1

        except HttpError as err:
            print(err)
