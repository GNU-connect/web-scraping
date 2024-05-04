import os
import pickle
import pytz
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.supabase_utils import supabase

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_12312231124-lis5fqh316vp0kq1o5qnqsr0cdeieh5a.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def clear_calendar(service, calendar_id):
    page_token = None
    try:
        while True:
            events_result = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
            events = events_result.get('items', [])
            for event in events:
                service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
            page_token = events_result.get('nextPageToken')
            if not page_token:
                break
    except HttpError as error:
        print(f'An error occurred: {error}')
        raise

def update_calendar_from_db(calendar_id_undergraduate, calendar_id_graduate):
    client = supabase()
    
    undergraduate_data = client.table('academic_calendar').select('*').eq('calendar_type', 1).execute().data
    graduate_data = client.table('academic_calendar').select('*').eq('calendar_type', 2).execute().data

    service = authenticate_google_calendar()
    
    clear_calendar(service, calendar_id_undergraduate)
    clear_calendar(service, calendar_id_graduate)

    add_events_to_calendar(service, calendar_id_undergraduate, undergraduate_data)
    
    add_events_to_calendar(service, calendar_id_graduate, graduate_data)

def add_events_to_calendar(service, calendar_id, data):
    seoul_tz = pytz.timezone('Asia/Seoul')
    for item in data:
        start_datetime = datetime.fromisoformat(item['start_date']).astimezone(seoul_tz)
        end_datetime = datetime.fromisoformat(item['end_date']).astimezone(seoul_tz)
        
        event = {
            'summary': item['content'],
            'start': {'dateTime': start_datetime.isoformat()},
            'end': {'dateTime': end_datetime.isoformat()},
        }
        try:
            service.events().insert(calendarId=calendar_id, body=event).execute()
        except HttpError as error:
            print(f"Failed to add event: {error}")
            continue
