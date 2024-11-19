from .scrapers import AcademicCalendarScraper, CafeteriaScraper
from .data_access.cafeteria_repository import get_cafeterias

def main():
    # 학사일정 스크래핑
    # academic_scraper = AcademicCalendarScraper()
    # academic_scraper.scrape_data()

    # 식당 메뉴 스크래핑
    cafeterias = get_cafeterias()
    for cafeteria in [cafeterias[0]]:
        cafeteria_scraper = CafeteriaScraper(cafeteria)
        cafeteria_scraper.scrape_data()

    # # 공지사항 스크래핑
    # notice_scraper = NoticeScraper("college_name")
    # notice_scraper.scrape_data()

if __name__ == "__main__":
    main()