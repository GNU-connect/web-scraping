from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# ChromeService 객체 생성
service = ChromeService(ChromeDriverManager().install())