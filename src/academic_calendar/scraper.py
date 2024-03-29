from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup
import traceback
from datetime import datetime, timedelta
from src.selenium_utils import get_driver

class Academic_Calendar_Scraper:
    def scrape_academic_calendar_data(self):
        base_url = 'https://www.gnu.ac.kr/main/ps/schdul/selectSchdulMainList.do?mi='
        try:
          driver = get_driver()
          driver.get(base_url)
          driver.implicitly_wait(3)
          parsed_html = driver.page_source
          
          parsed_html = BeautifulSoup(parsed_html, 'html.parser')

          tbody_element = parsed_html.find('tbody')
          a_elements = tbody_element.find_all('a')
          
          self.delete_schedules()
          result = []
          for a_element in a_elements:
            # href 속성에서 날짜 정보를 추출
            onclick_value = a_element['href']
            start_date = onclick_value.split("'")[3]
            start_date = datetime.strptime(start_date, '%Y/%m/%d')
            end_date = onclick_value.split("'")[5]
            end_date = datetime.strptime(end_date, '%Y/%m/%d')

            if end_date < datetime.now() - timedelta(days=1):
              continue

            # 텍스트에서 '2학기 동계방학' 추출
            contents = a_element.get_text()
            # 카테고리 추출
            category_idx = contents.find('-')
            category = contents[1:category_idx]
            content_idx = contents.find(']')
            if content_idx != -1:
              content = contents[content_idx + 1:].strip()
            else:
              continue
            
            schedule_object = {
              'calendar_type': 1 if category == '학부' else 2,
              'start_date': start_date.isoformat(),
              'end_date': end_date.isoformat(),
              'content': content
            }
            result.append(schedule_object)
          self.insert_schedules(result)
          print('[학사일정] 학사일정 데이터 교체 완료')

        except Exception as e:
          print(f'[학사일정] 학사일정 데이터 조회 실패: 학사일정 데이터를 가져오는데 실패했습니다.')
          print(f'[학사일정] 해당 학사일정 url: {base_url}')
          traceback.print_exc()
          return
    
    def insert_schedules(self, schedules):
      supabase().table('academic_calendar').insert(schedules).execute()
    
    def delete_schedules(self):
      supabase().table('academic_calendar').delete().neq('content', 0).execute()