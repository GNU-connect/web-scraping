from concurrent.futures import ThreadPoolExecutor, as_completed
from .scrapers import CafeteriaScraper
from .data_access.cafeteria_repository import get_cafeterias
from dotenv import load_dotenv

load_dotenv(verbose=True)

def scrape_cafeteria_data(cafeteria):
    """새로운 식당 데이터를 스크래핑하는 함수"""
    cafeteria_scraper = CafeteriaScraper(cafeteria)
    cafeteria_scraper.scrape_data()
    cafeteria_scraper.delete_past_data()

def main():
    cafeterias = get_cafeterias()

    with ThreadPoolExecutor(max_workers=5) as executor:  # 최대 스레드 수를 설정
        futures = [executor.submit(scrape_cafeteria_data, cafeteria) for cafeteria in cafeterias]

        # 작업 완료 상태 확인
        for future in as_completed(futures):
            try:
                future.result()  # 결과 확인 (예외 발생 시 처리)
            except Exception as e:
                print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
