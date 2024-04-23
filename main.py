import time
from multiprocessing import Pool
from src.notice.scraper import Notice_Scraper
from src.cafeteria.scraper import Cafeteria_Scraper
from src.academic_calendar.scraper import AcademicCalendarScraper
from src.supabase_utils import supabase
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

# 셀레니움 드라이버 로드
driver_path = ChromeDriverManager().install()

def delete_oldest_dishes():
    now_date = datetime.now() - timedelta(days=1)
    supabase().table('cafeteria-diet').delete().lt('date', now_date).execute()

def get_colleges():
    return [college['college_en'] for college in supabase().table('college').select('college_en, etc_value').execute().data if college['etc_value'] == False] + ['etc']

def get_cafeterias():
    return supabase().table('cafeteria').select('*').execute().data

def run_notice_scraper(college):
    notice_scraper = Notice_Scraper(college)
    notice_scraper.scrape_notice_data()

def run_cafeteria_scraper(cafeteria):
    cafeteria_scraper = Cafeteria_Scraper(driver_path, cafeteria)
    cafeteria_scraper.scrape_cafeteria_dish_data()

def run_academic_calendar_scraper():
    academic_calendar_scraper = AcademicCalendarScraper(driver_path)
    academic_calendar_scraper.scrape_academic_calendar_data()

if __name__ == '__main__':
    start_time = time.time()
    cafeterias = get_cafeterias()
    colleges = get_colleges()

    # 공지사항 스크래핑 작업
    with Pool() as pool:
       pool.map(run_notice_scraper, colleges)

    # 학사 일정 및 학식 스크래핑 작업
    delete_oldest_dishes()
    with Pool() as pool2:
        pool2.map(run_cafeteria_scraper, cafeterias)
        pool2.close()
        pool2.join()
    
    with Pool() as pool3:
       pool3.apply_async(run_academic_calendar_scraper)
       pool3.close()
       pool3.join()
    
    print(f"모든 웹페이지의 정보 스크래핑이 완료되었습니다. 소요시간: {time.time() - start_time:.2f}초")
