import os
import time
import uuid
from google.oauth2 import service_account
from googleapiclient.discovery import build

try:
    from src.firebase_config import admin_sdk_config
except ImportError:
    from firebase_config import admin_sdk_config

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')

# A bare service account cannot create Google Meet conferences or invite
# attendees — Google rejects both ("Service accounts cannot invite attendees
# without Domain-Wide Delegation of Authority"). To do either, the service
# account must act as a real Google Workspace user via domain-wide delegation.
# This is the email of that user (the calendar owner / tutor). Falls back to the
# calendar id (when it is an email) or the admin email.
CALENDAR_SUBJECT = (
    os.getenv('GOOGLE_CALENDAR_SUBJECT')
    or os.getenv('GOOGLE_IMPERSONATE_EMAIL')
    or (CALENDAR_ID if CALENDAR_ID and '@' in CALENDAR_ID else None)
    or os.getenv('ADMIN_EMAIL')
)


def _get_service():
    creds = service_account.Credentials.from_service_account_info(
        admin_sdk_config, scopes=SCOPES
    )
    # Impersonate the Workspace user so Meet links and attendee invites work.
    if CALENDAR_SUBJECT:
        creds = creds.with_subject(CALENDAR_SUBJECT)
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)


def _extract_meet_link(event):
    """Pull the video (Meet) URL out of an event's conferenceData, if present."""
    conference = event.get('conferenceData') or {}
    for ep in conference.get('entryPoints', []):
        if ep.get('entryPointType') == 'video':
            return ep.get('uri')
    return None


def create_lesson_event(date, start_time, end_time, student_email, student_name=""):
    """Create a Google Calendar event with a Meet link and invite the student.

    Returns {event_id, meet_link, html_link} or None if calendar is not
    configured. Raises on API errors so the caller can record why it failed.
    """
    # Impersonated subject owns a "primary" calendar we can fall back to.
    target_calendar = CALENDAR_ID or ('primary' if CALENDAR_SUBJECT else None)
    if not target_calendar:
        return None

    service = _get_service()

    start_dt = f"{date}T{start_time}:00"
    end_dt = f"{date}T{end_time}:00"

    display = student_name or student_email

    event = {
        'summary': f"Tutoring: {display}",
        'description': f'1-on-1 programming tutoring session with {display}',
        'start': {
            'dateTime': start_dt,
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': end_dt,
            'timeZone': 'Europe/London',
        },
        'attendees': [{'email': student_email}] if student_email else [],
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
        calendarId=target_calendar,
        body=event,
        conferenceDataVersion=1,
        sendUpdates='all',  # emails the Meet invite to the student
    ).execute()

    meet_link = _extract_meet_link(created)

    # The Meet conference can still be provisioning immediately after insert;
    # re-fetch the event a few times until the link appears.
    attempts = 0
    while not meet_link and attempts < 3:
        time.sleep(1)
        attempts += 1
        refreshed = service.events().get(
            calendarId=target_calendar,
            eventId=created['id'],
        ).execute()
        meet_link = _extract_meet_link(refreshed)

    return {
        'event_id': created.get('id'),
        'meet_link': meet_link,
        'html_link': created.get('htmlLink'),
    }
