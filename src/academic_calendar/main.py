import time
from .scraper import Academic_Calendar_Scraper

if __name__ == '__main__':
  start_time = time.time()
  # 학사일정 데이터 스크래핑
  academic_calendar_scraper = Academic_Calendar_Scraper()
  academic_calendar_scraper.scrape_academic_calendar_data()

  print(f"모든 학사일정 스크래핑이 완료되었습니다. 소요시간: {time.time() - start_time}초")