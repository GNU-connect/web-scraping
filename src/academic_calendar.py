from .scrapers.academic_calendar import AcademicCalendarScraper
from dotenv import load_dotenv
load_dotenv(verbose=True)

def main():
    academic_scraper = AcademicCalendarScraper()
    academic_scraper.scrape_data()

if __name__ == "__main__":
    main()