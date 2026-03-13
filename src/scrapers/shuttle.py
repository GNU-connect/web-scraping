import re
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from ..scrapers.base import RequestScraper
from ..models.shuttle import ShuttleTimetable

SHUTTLE_URL = 'https://www.gnu.ac.kr/main/cm/cntnts/cntntsView.do?mi=1358&cntntsId=1194'


class ShuttleScraper(RequestScraper):
    def __init__(self, repository=None):
        super().__init__(base_url=SHUTTLE_URL)
        if repository is not None:
            self.repository = repository
        else:
            from ..data_access.shuttle_repository import ShuttleRepository
            self.repository = ShuttleRepository()

    def get_scraper_name(self) -> str:
        return '셔틀버스'

    def scrape_data(self) -> None:
        try:
            soup = self.parsed_html(self.base_url)
            routes = self._parse_routes(soup)
            for route in routes:
                self.repository.upsert_timetable(route)
            print(f'[셔틀버스] {len(routes)}개 노선 시간표 저장 완료')
        except Exception as e:
            self.notify_failure(e, '셔틀버스 시간표 스크래핑 실패')

    def _parse_routes(self, soup: BeautifulSoup) -> List[ShuttleTimetable]:
        updated_at = self._parse_updated_at(soup)
        return [
            ShuttleTimetable(
                route_name=self._parse_route_name(table),
                timetable=self._parse_timetable(table),
                updated_at=updated_at,
            )
            for table in soup.find_all('table')
        ]

    def _parse_route_name(self, table: BeautifulSoup) -> str:
        caption = table.find('caption')
        if caption:
            raw = caption.get_text(strip=True)
        else:
            first_th = table.find('th')
            raw = first_th.get_text(strip=True) if first_th else ''
        return re.sub(r'\(.*?\)', '', raw).strip()

    def _parse_timetable(self, table: BeautifulSoup) -> dict:
        header_row = [tr for tr in table.find_all('tr') if tr.find('th')][-1]
        headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        timetable = {header: [] for header in headers}

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if not cells:
                continue
            for idx, header in enumerate(headers):
                if idx >= len(cells):
                    continue
                time_text = self._normalize_time(cells[idx].get_text(strip=True))
                if time_text:
                    timetable[header].append(time_text)

        return timetable

    def _normalize_time(self, raw: str) -> str:
        return re.sub(r'\s*:\s*', ':', raw).strip()

    def _parse_updated_at(self, soup: BeautifulSoup) -> datetime:
        pattern = r'최근 업데이트 일시\s*:\s*(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})'
        text = soup.get_text()
        match = re.search(pattern, text)
        if not match:
            raise ValueError('업데이트 일시를 찾을 수 없습니다.')
        return datetime.strptime(match.group(1), '%Y/%m/%d %H:%M:%S')
