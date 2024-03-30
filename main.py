import time
from src.notice.scraper import Notice_Scraper
from src.cafeteria.scraper import Cafeteria_Scraper
from src.academic_calendar.scraper import AcademicCalendarScraper
from multiprocessing import Process
from src.supabase_utils import supabase
import src.selenium_utils

def get_colleges():
    colleges = supabase().table('college').select('college_en, etc_value').execute().data
    college_en_list = [college['college_en'] for college in colleges if college['etc_value'] == False]
    college_en_list.append('etc')
    return college_en_list

def run_notice_scraper(college):
    notice_scraper = Notice_Scraper(college)
    notice_scraper.scrape_notice_data()

def run_cafeteria_scraper():
    cafeteria_scraper = Cafeteria_Scraper()
    cafeteria_scraper.delete_oldest_dishes()
    cafeteria_scraper.scrape_cafeteria_dish_data()

def run_academic_calendar_scraper():
    academic_calendar_scraper = AcademicCalendarScraper()
    academic_calendar_scraper.scrape_academic_calendar_data()

if __name__ == '__main__':
    start_time = time.time()
    colleges = get_colleges()

    processes = []
    # 단과대학별 공지사항 스크래핑
    for college in colleges:
        process = Process(target=run_notice_scraper, args=(college,))
        processes.append(process)
        process.start()
    # 학식 데이터 스크래핑
    process = Process(target=run_cafeteria_scraper)
    processes.append(process)
    process.start()
    # 학사일정 데이터 스크래핑
    process = Process(target=run_academic_calendar_scraper)
    processes.append(process)
    process.start()
    
    for process in processes:
        process.join()
    
    print(f"모든 웹페이지의 정보 스크래핑이 완료되었습니다. 소요시간: {time.time() - start_time}초")