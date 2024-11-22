from .base import SeleniumScraper
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from ..config.settings import ACADEMIC_CALENDAR_URL
from typing import List
from ..models.academic_calendar import AcademicCalendar
from ..data_access.academic_calendar_repository import insert_schedules, delete_schedules

class AcademicCalendarScraper(SeleniumScraper):
    def __init__(self):
        super().__init__(base_url=ACADEMIC_CALENDAR_URL)

    def get_scraper_name(self):
        return "학사일정"

    def check_duplicate(self, schedule_object, result):
        return any(
            item['calendar_type'] == schedule_object['calendar_type'] and
            item['start_date'] == schedule_object['start_date'] and
            item['end_date'] == schedule_object['end_date'] and
            item['content'] == schedule_object['content']
            for item in result
        )

    def scrape_data(self):
        try:
            with self as scraper:
                scraper.driver.get(self.base_url)
                time.sleep(2)
                result: List[AcademicCalendar] = []
                
                for _ in range(2):  # 올해, 내년 학사일정
                    self._process_current_page(result)
                    self._click_next_year()
                
                delete_schedules()
                insert_schedules(result)
                print('[학사일정] 학사일정 데이터 교체 완료')

        except Exception as e:
            self.notify_failure(e, "학사일정 데이터 조회 실패")

    def _process_current_page(self, result):
        parsed_html = BeautifulSoup(self.driver.page_source, 'html.parser')
        tbody_element = parsed_html.find('tbody')
        a_elements = tbody_element.find_all('a')

        for a_element in a_elements:
            schedule = self._extract_schedule(a_element)
            if schedule and not self.check_duplicate(schedule, result):
                result.append(schedule)

    def _extract_schedule(self, a_element):
        onclick_value = a_element['href']
        start_date = datetime.strptime(onclick_value.split("'")[3], '%Y/%m/%d')
        end_date = datetime.strptime(onclick_value.split("'")[5], '%Y/%m/%d')

        if end_date < datetime.now() - timedelta(days=1):
            return None

        contents = a_element.get_text()
        category_idx = contents.find('-')
        category = contents[1:category_idx]
        content_idx = contents.find(']')
        
        if content_idx == -1:
            return None

        content = contents[content_idx + 1:].strip()
        return {
            'calendar_type': 1 if category == '학부' else 2,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'content': content
        }

    def _click_next_year(self):
        next_year_button = self.driver.find_element(
            By.XPATH, '//*[@id="listForm"]/div/div[1]/div[1]/a[3]/i'
        )
        next_year_button.click()
        time.sleep(2)