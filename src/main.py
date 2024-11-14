from scrapers import AcademicCalendarScraper, CafeteriaScraper, NoticeScraper
from config.settings import CHROME_DRIVER_PATH

def main():
    # 학사일정 스크래핑
    academic_scraper = AcademicCalendarScraper(CHROME_DRIVER_PATH)
    academic_scraper.scrape_data()

    # 식당 메뉴 스크래핑
    cafeteria_scraper = CafeteriaScraper(CHROME_DRIVER_PATH)
    cafeteria_scraper.scrape_data()

    # 공지사항 스크래핑
    notice_scraper = NoticeScraper("college_name")
    notice_scraper.scrape_data()

if __name__ == "__main__":
    main()