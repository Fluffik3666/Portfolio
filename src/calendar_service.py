import os
import uuid
from google.oauth2 import service_account
from googleapiclient.discovery import build

try:
    from src.firebase_config import admin_sdk_config
except ImportError:
    from firebase_config import admin_sdk_config

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')


def _get_service():
    creds = service_account.Credentials.from_service_account_info(
        admin_sdk_config, scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)


def create_lesson_event(date, start_time, end_time, student_email, student_name=""):
    """Create a Google Calendar event with a Meet link.
    Returns the Meet link URL or None if calendar is not configured.
    """
    if not CALENDAR_ID:
        return None

    service = _get_service()

    start_dt = f"{date}T{start_time}:00"
    end_dt = f"{date}T{end_time}:00"

    summary = f"Tutoring: {student_name or student_email}"

    event = {
        'summary': summary,
        'description': f'1-on-1 programming tutoring session with {student_name or student_email}',
        'start': {
            'dateTime': start_dt,
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': end_dt,
            'timeZone': 'Europe/London',
        },
        'attendees': [
            {'email': student_email},
        ],
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            },
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 60},
                {'method': 'popup', 'minutes': 15},
            ],
        },
    }

    created = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
        conferenceDataVersion=1,
        sendUpdates='all',  # sends invite email to attendees
    ).execute()

    meet_link = None
    if created.get('conferenceData') and created['conferenceData'].get('entryPoints'):
        for ep in created['conferenceData']['entryPoints']:
            if ep.get('entryPointType') == 'video':
                meet_link = ep.get('uri')
                break

    return {
        'event_id': created.get('id'),
        'meet_link': meet_link,
        'html_link': created.get('htmlLink'),
    }
