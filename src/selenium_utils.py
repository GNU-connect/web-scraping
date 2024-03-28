from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def get_driver():
    # headless 모드를 사용하기 위해 옵션 객체 생성
    options = Options()
    options.add_argument("headless")

    # ChromeService 객체 생성
    service = ChromeService(ChromeDriverManager().install())

    # Chrome WebDriver에 옵션 적용
    driver = webdriver.Chrome(service=service, options=options)
    return driver