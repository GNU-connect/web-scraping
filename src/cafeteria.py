from .scrapers import CafeteriaScraper
from .data_access.cafeteria_repository import CafeteriaRepository
from dotenv import load_dotenv

load_dotenv(verbose=True)


def main():
    repository = CafeteriaRepository()
    cafeterias = repository.get_cafeterias()

    for cafeteria in cafeterias:
        scraper = CafeteriaScraper(cafeteria, repository)
        scraper.scrape_data(save_data=True)


if __name__ == "__main__":
    main()
