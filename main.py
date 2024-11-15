from multiprocessing import Pool
import sentry_sdk
from sentry_sdk.crons import monitor
import os
from src.notice.scraper import Notice_Scraper
from src.cafeteria.scraper import Cafeteria_Scraper
from src.news.scraper import News_Scraper
from src.academic_calendar.scraper import AcademicCalendarScraper
from src.utils.supabase import get_supabase_client
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv(verbose=True)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
)

# 셀레니움 드라이버 로드
driver_path = ChromeDriverManager().install()

def delete_oldest_dishes():
    now_date = datetime.now() - timedelta(days=1)
    get_supabase_client().table('cafeteria_diet').delete().lt('date', now_date).execute()

def get_colleges():
    return [college['college_en'] for college in get_supabase_client().table('college').select('college_en, etc_value').execute().data if college['etc_value'] == False] + ['etc']

def get_cafeterias():
    return get_supabase_client().table('cafeteria').select('*').execute().data

def run_news_scraper():
    news_scraper = News_Scraper()
    news_scraper.scrape_news_data()

def run_notice_scraper(college):
    notice_scraper = Notice_Scraper(college)
    notice_scraper.scrape_notice_data()

def run_cafeteria_scraper(cafeteria):
    cafeteria_scraper = Cafeteria_Scraper(driver_path, cafeteria)
    cafeteria_scraper.scrape_cafeteria_dish_data()

def run_academic_calendar_scraper():
    academic_calendar_scraper = AcademicCalendarScraper(driver_path)
    academic_calendar_scraper.scrape_academic_calendar_data()

@monitor(monitor_slug='python-web-scraper')
def main():
    cafeterias = get_cafeterias()
    colleges = get_colleges()

    delete_oldest_dishes()

    run_news_scraper()
    with Pool() as pool:
        pool.map(run_notice_scraper, colleges)
        pool.map(run_cafeteria_scraper, cafeterias)
        academic_calendar = pool.apply_async(run_academic_calendar_scraper)
        academic_calendar.wait()  # 비동기 작업이 완료될 때까지 기다림

if __name__ == '__main__':
    main()
