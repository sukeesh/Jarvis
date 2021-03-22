from plugin import plugin
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__))[:len(
    os.path.dirname(os.path.realpath(__file__))) - len('/jarviscli/plugins')], 'credentials.json')

def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

@plugin("google calendar")
def GoogleCalendar(jarvis, s):
    '''
    Gives you the s next events of your calendar 
    '''
    if (int(s) > 0):
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting List of ' + s + ' events')
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=int(s), singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get(
                'dateTime', event['start'].get('date')).split('T')[0]
            print(start, event['summary'])
            