from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import traceback
from datetime import datetime, timedelta
from src.utils.supabase import get_supabase_client
from selenium.webdriver.chrome.service import Service as ChromeService
from src.utils.slack import Slack_Notifier

class AcademicCalendarScraper:
    def __init__(self, driver_path):
        self.base_url = 'https://www.gnu.ac.kr/main/ps/schdul/selectSchdulMainList.do?mi='
        self.driver_path = driver_path
        self.driver = None

    def __enter__(self):
        options = Options()
        options.add_argument("headless")
        service = ChromeService(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()
    
    def scrape_academic_calendar_data(self):
        def check_duplicate(schedule_object, result):
            for item in result:
                if (item['calendar_type'] == schedule_object['calendar_type'] and
                    item['start_date'] == schedule_object['start_date'] and
                    item['end_date'] == schedule_object['end_date'] and
                    item['content'] == schedule_object['content']):
                    return True
            return False
        
        try:
            with self as scraper:
                scraper.driver.get(self.base_url)
                time.sleep(1)
                result = []
                # 올해, 내년 학사일정 데이터를 가져오기 위해 2번 반복
                for _ in range(2):
                    parsed_html = BeautifulSoup(scraper.driver.page_source, 'html.parser')

                    tbody_element = parsed_html.find('tbody')
                    a_elements = tbody_element.find_all('a')

                    for a_element in a_elements:
                        # href 속성에서 날짜 정보를 추출
                        onclick_value = a_element['href']
                        start_date = datetime.strptime(onclick_value.split("'")[3], '%Y/%m/%d')
                        end_date = datetime.strptime(onclick_value.split("'")[5], '%Y/%m/%d')

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
                        if not check_duplicate(schedule_object, result):
                            result.append(schedule_object)
                    next_year_button = self.driver.find_element(By.XPATH, '//*[@id="listForm"]/div/div[1]/div[1]/a[3]/i')
                    next_year_button.click()
                    time.sleep(1)

                self.delete_schedules()
                self.insert_schedules(result)
                print('[학사일정] 학사일정 데이터 교체 완료')

        except Exception as e:
            print(f'[학사일정] 학사일정 데이터 조회 실패: 학사일정 데이터를 {e}의 사유로 가져오는데 실패했습니다.')
            print(f'[학사일정] 해당 학사일정 url: {self.base_url}')
            Slack_Notifier().fail(f'학사일정 데이터 조회 실패: 학사일정 데이터를 {e}의 사유로 가져오는데 실패했습니다. \n \
                                    해당 학사일정 url: {self.base_url}')
            traceback.print_exc()

    def insert_schedules(self, schedules):
        get_supabase_client().table('academic_calendar').insert(schedules).execute()

    def delete_schedules(self):
        get_supabase_client().table('academic_calendar').delete().neq('content', 0).execute()
