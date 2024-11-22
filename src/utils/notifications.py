import requests
import os

class Slack_Notifier:
    def __init__(self):
        # Slack 웹훅 URL 환경 변수에서 가져오기
        self.url = os.getenv("SLACK_WEBHOOK_URL")
        # HTTP 헤더 설정
        self.channel = '#web-scraping-notification'
        self.headers = {
            'Content-Type': 'application/json',
        }
    
    def success(self, time=None, logs=None):
        # 성공 메시지 생성
        data = {
            'channel': self.channel,
            'attachments': [
                {
                    'color': '#2EB886',  # 초록색
                    'fields': [
                        {
                            'title': '🔎 웹페이지 정보 스크래핑 완료',
                            'value': f'지누 친구가 새로운 정보들을 가득 들고왔어! {time:.2f}초가 소요됐어.',
                            'short': False
                        },
                        {
                            'title': '로그',
                            'value': logs,
                            'short': False
                        }
                    ]
                }
            ]
        }
        # Slack에 메시지 보내기
        response = requests.post(self.url, headers=self.headers, json=data)
        
        # 응답 상태 코드 확인
        if response.status_code != 200:
            print('Failed to send success notification:', response.status_code, response.text)
    
    def fail(self, error_message=None):
        # 실패 메시지 생성
        data = {
            'channel': self.channel,
            'attachments': [
                {
                    'color': '#FF0000',  # 빨간색
                    'title': '❌ 웹페이지 정보 스크래핑 실패',
                    'text': f'<!here> {error_message}',
                }
            ]
        }
        # Slack에 메시지 보내기
        response = requests.post(self.url, headers=self.headers, json=data)
        
        # 응답 상태 코드 확인
        if response.status_code != 200:
            print('Failed to send success notification:', response.status_code, response.text)