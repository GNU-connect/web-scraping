from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import traceback
from ..config.settings import CHROME_DRIVER_PATH
import requests
from bs4 import BeautifulSoup
from ..utils.notifications import Slack_Notifier


class BaseScraper(ABC):
    def __init__(self):
        self.base_url = None

    def notify_failure(self, error, context_message):
        """공통 에러 처리 및 알림 메서드"""
        error_message = f'{context_message}: {str(error)}'
        print(f'[{self.get_scraper_name()}] {error_message}')
        print(f'[{self.get_scraper_name()}] URL: {self.base_url}')
        # Slack_Notifier().fail(f'{error_message}\nURL: {self.base_url}')
        traceback.print_exc()

    @abstractmethod
    def get_scraper_name(self):
        """스크래퍼 이름을 반환하는 메서드"""
        pass

    @abstractmethod
    def scrape_data(self):
        """데이터를 스크래핑하는 메서드"""
        pass


class SeleniumScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__()
        self.driver_path = CHROME_DRIVER_PATH
        self.base_url = base_url

    def __enter__(self):
        if hasattr(self, 'driver_path'):
            options = Options()
            options.add_argument('headless')
            service = ChromeService(self.driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()


class RequestScraper(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def parsed_html(self, url: str) -> BeautifulSoup:
        try:
            request = requests.get(url)
            return BeautifulSoup(request.text, 'html.parser')
        except Exception as e:
            ValueError(f'HTML 파싱 실패: {str(e)}')
