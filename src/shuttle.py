from .scrapers.shuttle import ShuttleScraper
from dotenv import load_dotenv

load_dotenv(verbose=True)


def main():
    scraper = ShuttleScraper()
    scraper.scrape_data()


if __name__ == "__main__":
    main()
