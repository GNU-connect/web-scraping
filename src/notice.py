from .scrapers.notice import NoticeScraper
import time


def main():
    threads_start = time.time()
    notice_scraper = NoticeScraper()
    notice_scraper.scrape_data(use_multithreading=True)
    threads_end = time.time()

    print(f"소요 시간: {threads_end - threads_start:.2f}초")


if __name__ == "__main__":
    main()
