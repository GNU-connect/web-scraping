from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import traceback
from ..config.settings import CHROME_DRIVER_PATH
from ..utils.notifications import send_slack_notification

class BaseScraper(ABC):
    def __init__(self):
        self.base_url = None
    
    def notify_failure(self, error, context_message):
        """공통 에러 처리 및 알림 메서드"""
        error_message = f'{context_message}: {str(error)}'
        print(f'[{self.get_scraper_name()}] {error_message}')
        print(f'[{self.get_scraper_name()}] URL: {self.base_url}')
        #send_slack_notification().fail(f'{error_message}\nURL: {self.base_url}')
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
    