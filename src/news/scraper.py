from src.utils.supabase import get_supabase_client
import requests
from bs4 import BeautifulSoup
import traceback
from src.utils.slack import Slack_Notifier

class News_Scraper:
    def scrape_news_data(self):
          base_url = "https://www.gnunews.kr/"

          try:
              request = requests.get(base_url)
              parsed_html = BeautifulSoup(request.text, 'html.parser')
              target_section = parsed_html.select_one('#idx14 > div:nth-of-type(3) > div:nth-of-type(2) > div:nth-of-type(4) > div > article > section')
              # 모든 item 요소를 찾기
              items = target_section.find_all('div', class_='item')

              # 등록 시간과 제목 추출
              result = []
              for item in items[:5]:
                  registration_time = item.find('em', class_='auto-times').text
                  title = item.find('span', class_='auto-titles').text
                  url = base_url[:-1] + item.find('a')['href']
                  news_object = {
                      'registration_time': registration_time,
                      'title': title,
                      'url': url
                  }
                  result.append(news_object)
              
              if len(result) > 0:
                self.delete_news_data()
                self.insert_news_data(result)

          except Exception as e:
              print(f'[경대뉴스] 경대뉴스 데이터 조회 실패: {e} 의 사유로 실패했습니다.')
              Slack_Notifier().fail(f'경대뉴스 데이터 조회 실패: {e} 의 사유로 실패했습니다.')
              traceback.print_exc()
    
    def delete_news_data(self):
        get_supabase_client().table('news').delete().neq('title', 0).execute()
    
    def insert_news_data(self, news_datas):
        get_supabase_client().table('news').insert(news_datas).execute()