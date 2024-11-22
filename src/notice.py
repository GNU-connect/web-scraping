from concurrent.futures import ThreadPoolExecutor, as_completed
from .scrapers.notice import NoticeScraper
from .data_access.base_repository import get_colleges
from dotenv import load_dotenv
from typing import List
from .models.base import College

load_dotenv(verbose=True)


def scrape_college_data(college: College):
    """단과대학 별 공지사항 데이터를 스크래핑하는 함수"""
    notice_scraper = NoticeScraper(college)
    notice_scraper.scrape_data()


def main():
    colleges: List[College] = get_colleges()

    # ThreadPoolExecutor로 멀티스레드 처리
    with ThreadPoolExecutor(max_workers=10) as executor:  # 최대 스레드 수를 적절히 설정
        futures = [executor.submit(scrape_college_data, college) for college in colleges]

        # 작업 완료 상태 확인
        for future in as_completed(futures):
            try:
                future.result()  # 결과 확인 (예외가 있으면 여기서 처리됨)
            except Exception as e:
                print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
