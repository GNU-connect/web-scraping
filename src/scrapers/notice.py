from ..scrapers.base import RequestScraper
from ..data_access.notice_repository import get_notice_categories, get_category_notices, insert_notices, update_notice, update_category_last_ntt_sn
from typing import List, Optional
from ..models.notice import Notice, NoticeCategory
from datetime import datetime
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


class NoticeScraper(RequestScraper):
    MAX_NOTICES = 5
    MAX_NOTICE_AGE_DAYS = 30

    def __init__(self):
        super().__init__(base_url=None)

    def get_scraper_name(self) -> str:
        return '공지사항'

    def scrape_data(self, use_multithreading=False) -> None:
        """메인 스크래핑 프로세스를 실행합니다."""
        categories = get_notice_categories()

        # 멀티스레딩 사용 여부에 따라 스크래핑 방식을 변경
        if use_multithreading:
            cpu_count = os.cpu_count()
            max_workers = cpu_count * 5

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self._process_category, category)
                           for category in categories]

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.notify_failure(e, "공지사항 데이터 조회 실패")
        else:
            for category in categories:
                self._process_category(category)

    def _process_category(self, category: NoticeCategory) -> None:
        """각 카테고리의 공지사항을 처리합니다."""
        base_url = self._get_base_url(
            category.department_en, category.mi, category.bbs_id)

        try:
            new_notices = self._scrape_notices(base_url, category)
            if new_notices:
                self._update_notices(category, new_notices)
                print(f"[공지사항] {category.department_ko}의 {category.category} "
                      f"카테고리의 새로운 공지사항 {len(new_notices)}개를 스크래핑했습니다.")

        except Exception as e:
            self.notify_failure(
                e, f"{category.department_ko}의 {category.category} 카테고리 스크래핑에 실패했습니다.")

    def _scrape_notices(self, url: str, category: NoticeCategory) -> List[Notice]:
        result: List[Notice] = []

        soup = self.parsed_html(url)

        headers = [th.text.strip() for th in soup.find('thead').find_all('th')]
        notice_rows = soup.find('tbody').find_all('tr')
        date_idx = headers.index('등록일')

        for row in notice_rows:
            notice = self._parse_notice_row(row, date_idx, category)
            if notice and self._is_valid_notice(notice, category.last_ntt_sn):
                result.append(notice)

        return sorted(result, key=lambda x: x.ntt_sn, reverse=True)[:self.MAX_NOTICES]

    def _get_base_url(self, department_en: str, mi: int, bbs_id: int) -> str:
        return f'https://www.gnu.ac.kr/{department_en}/na/ntt/selectNttList.do?mi={mi}&bbsId={bbs_id}'

    def _parse_notice_row(self, row: BeautifulSoup, date_idx: int, category: NoticeCategory) -> Optional[Notice]:
        """공지사항 행을 파싱합니다."""
        try:
            ntt_sn = int(row.find('a', class_='nttInfoBtn')['data-id'])
            date_str = row.find_all('td')[date_idx].text.strip()
            date = datetime.strptime(date_str, '%Y.%m.%d')
            title = row.find('a').contents[0].strip()

            return Notice(
                category_id=category.id,
                title=title,
                ntt_sn=ntt_sn,
                created_at=date.isoformat()
            )
        except Exception:
            return None

    def _is_valid_notice(self, notice: Notice, last_ntt_sn: int) -> bool:
        """공지사항이 유효한지 확인합니다."""
        notice_date = datetime.fromisoformat(notice.created_at)
        is_new = notice.ntt_sn > last_ntt_sn
        is_recent = (datetime.now() -
                     notice_date).days <= self.MAX_NOTICE_AGE_DAYS
        return is_new and is_recent

    def _update_notices(self, category: NoticeCategory, new_notices: List[Notice]) -> None:
        """공지사항을 데이터베이스에 업데이트합니다."""
        existing_notices = get_category_notices(category.id)
        empty_space = self.MAX_NOTICES - len(existing_notices)

        # 새 공지사항 삽입
        if empty_space > 0:
            insert_notices(new_notices[:empty_space])

        # 기존 공지사항 업데이트
        for i, notice in enumerate(new_notices[empty_space:]):
            update_notice(notice, existing_notices[i]['id'])

        # 마지막 공지사항 번호 업데이트
        update_category_last_ntt_sn(
            category.id, new_notices[0].ntt_sn)
