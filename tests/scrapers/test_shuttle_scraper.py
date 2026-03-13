from datetime import datetime
from unittest.mock import MagicMock
import pytest
from bs4 import BeautifulSoup

from src.scrapers.shuttle import ShuttleScraper
from src.models.shuttle import ShuttleTimetable

FIXTURE_HTML = """
<html>
<body>
<div class="contents">
  <table>
    <thead></thead>
    <tbody>
      <tr><th colspan="2">가좌캠퍼스 → 칠암캠퍼스(출발지: 가좌캠퍼스)</th></tr>
      <tr><th>오전</th><th>오후</th></tr>
    </tbody>
    <tbody>
      <tr><td>08 : 20</td><td>13 : 10 (금요일 미운행)</td></tr>
      <tr><td>09 : 00 (금요일 미운행)</td><td>13 : 40</td></tr>
      <tr><td>09 : 30</td><td>13 : 50</td></tr>
      <tr><td></td><td>14 : 00</td></tr>
    </tbody>
  </table>

  <table>
    <thead>
      <tr><th colspan="2">칠암캠퍼스 → 가좌캠퍼스(출발지: 칠암캠퍼스)</th></tr>
      <tr><th>오전</th><th>오후</th></tr>
    </thead>
    <tbody>
      <tr><td>08 : 05</td><td>13 : 00</td></tr>
      <tr><td>08 : 10</td><td>13 : 10</td></tr>
      <tr><td>08 : 30 (금요일 미운행)</td><td>13 : 40 (금요일 미운행)</td></tr>
      <tr><td></td><td>17 : 00</td></tr>
    </tbody>
  </table>

  <p>최근 업데이트 일시 : 2026/03/13 09:47:30</p>
</div>
</body>
</html>
"""


@pytest.fixture
def scraper():
    mock_repository = MagicMock()
    return ShuttleScraper(repository=mock_repository)


@pytest.fixture
def soup():
    return BeautifulSoup(FIXTURE_HTML, "html.parser")


class TestParseRouteName:
    def test_parse_route_name_가좌_to_칠암(self, scraper, soup):
        table = soup.find_all("table")[0]
        assert scraper._parse_route_name(table) == "가좌캠퍼스 → 칠암캠퍼스"

    def test_parse_route_name_칠암_to_가좌(self, scraper, soup):
        table = soup.find_all("table")[1]
        assert scraper._parse_route_name(table) == "칠암캠퍼스 → 가좌캠퍼스"

    def test_parse_route_name_removes_parenthesis_suffix(self, scraper, soup):
        table = soup.find_all("table")[0]
        route_name = scraper._parse_route_name(table)
        assert "(출발지:" not in route_name


class TestParseTimetable:
    def test_parse_timetable_normalizes_time_format(self, scraper, soup):
        table = soup.find_all("table")[0]
        timetable = scraper._parse_timetable(table)
        assert "08:20" in timetable["오전"]

    def test_parse_timetable_preserves_friday_annotation(self, scraper, soup):
        table = soup.find_all("table")[0]
        timetable = scraper._parse_timetable(table)
        assert "09:00 (금요일 미운행)" in timetable["오전"]
        assert "13:10 (금요일 미운행)" in timetable["오후"]

    def test_parse_timetable_excludes_empty_cells(self, scraper, soup):
        table = soup.find_all("table")[0]
        timetable = scraper._parse_timetable(table)
        assert "" not in timetable["오전"]
        assert "" not in timetable["오후"]

    def test_parse_timetable_keys_are_only_오전_오후(self, scraper, soup):
        table = soup.find_all("table")[0]
        timetable = scraper._parse_timetable(table)
        assert set(timetable.keys()) == {"오전", "오후"}

    def test_parse_timetable_returns_correct_오전_count(self, scraper, soup):
        table = soup.find_all("table")[0]
        timetable = scraper._parse_timetable(table)
        assert len(timetable["오전"]) == 3

    def test_parse_timetable_returns_correct_오후_count(self, scraper, soup):
        table = soup.find_all("table")[0]
        timetable = scraper._parse_timetable(table)
        assert len(timetable["오후"]) == 4


class TestParseUpdatedAt:
    def test_parse_updated_at_returns_datetime(self, scraper, soup):
        result = scraper._parse_updated_at(soup)
        assert isinstance(result, datetime)

    def test_parse_updated_at_correct_value(self, scraper, soup):
        result = scraper._parse_updated_at(soup)
        assert result == datetime(2026, 3, 13, 9, 47, 30)


class TestScrapeData:
    def test_scrape_data_returns_two_routes(self, scraper, soup):
        routes = scraper._parse_routes(soup)
        assert len(routes) == 2

    def test_scrape_data_routes_are_shuttle_timetable(self, scraper, soup):
        routes = scraper._parse_routes(soup)
        assert all(isinstance(r, ShuttleTimetable) for r in routes)

    def test_scrape_data_calls_repository_upsert_twice(self, scraper, mocker):
        mocker.patch.object(scraper, "parsed_html", return_value=BeautifulSoup(
            FIXTURE_HTML, "html.parser"))
        scraper.scrape_data()
        assert scraper.repository.upsert_timetable.call_count == 2

    def test_scrape_data_passes_correct_route_names(self, scraper, mocker):
        mocker.patch.object(scraper, "parsed_html", return_value=BeautifulSoup(
            FIXTURE_HTML, "html.parser"))
        scraper.scrape_data()
        call_args = [
            call.args[0].route_name for call in scraper.repository.upsert_timetable.call_args_list]
        assert "가좌캠퍼스 → 칠암캠퍼스" in call_args
        assert "칠암캠퍼스 → 가좌캠퍼스" in call_args
