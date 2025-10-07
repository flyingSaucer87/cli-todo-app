from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google():
    """Handles authentication with Google Calendar API."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def add_to_calendar(task_name, due_date_obj):
    """Adds a task to the Google Calendar as an all-day event."""
    try:
        creds = authenticate_google()
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": task_name,
            "description": "Task added from CLI Todo App",
            "start": {
                "date": due_date_obj.isoformat(),
            },
            "end": {
                "date": due_date_obj.isoformat(),
            },
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"✅ Event created: {created_event.get('htmlLink')}")

    except HttpError as error:
        raise Exception(f"An API error occurred: {error}")
    except Exception as e:
        raise e

def fetch_upcoming_events(max_results=10):
    """Fetches the next N upcoming events from the primary calendar."""
    try:
        creds = authenticate_google()
        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])

    except HttpError as error:
        print(f'An error occurred while fetching events: {error}')
        return None