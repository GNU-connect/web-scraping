import os
import pickle
import pytz
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils.supabase import get_supabase_client

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
            # 환경 변수에서 JSON 문자열을 가져오기
            client_secret_json_str = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
            
            # JSON 문자열을 파이썬 딕셔너리로 변환
            client_secret_data = json.loads(client_secret_json_str)
            
            # from_client_config를 사용하여 인증 흐름 생성
            flow = InstalledAppFlow.from_client_config(client_secret_data, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def update_icalendar_from_db():
    def get_ical_url(calendar_id):
      return f"https://calendar.google.com/calendar/ical/{calendar_id}/public/basic.ics"

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
    
    def get_academic_calendar_data(calendar_type):
      return get_supabase_client().table('academic_calendar').select('*').eq('calendar_type', calendar_type).execute().data
    
    def delete_all_events(service, calendar_id):
        events = service.events().list(calendarId=calendar_id).execute()
        if 'items' in events:
            for event in events['items']:
                service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()

    try:
      service = authenticate_google_calendar()

      # 경상대 학부생 학사일정
      calendar_undergraduate_id = os.getenv("GOOGLE_CALENDAR_UNDERGRADUATE_ID")
      print(f"Updating icalendar: {calendar_undergraduate_id}")
      delete_all_events(service, calendar_undergraduate_id)
      undergraduate_data = get_academic_calendar_data(1)
      add_events_to_calendar(service, calendar_undergraduate_id, undergraduate_data)

      return get_ical_url(calendar_undergraduate_id)
    except Exception as e:
      print(f'Failed to update icalendar: {e}')
      return None
