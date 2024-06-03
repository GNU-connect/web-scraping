from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from src.utils.slack import Slack_Notifier
import traceback
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase_client: Client = create_client(url, key)

# 셀레니움 드라이버 로드
driver_path = ChromeDriverManager().install()
bucket = 'clicker'

class ClickerScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

    def __enter__(self):
        options = Options()
        options.add_argument("--headless=new")  # 최신 헤드리스 모드 사용
        options.add_argument("--disable-gpu")  # GPU 사용 비활성화 (일부 환경에서 필요)
        options.add_argument("--no-sandbox")  # 샌드박스 비활성화 (일부 환경에서 필요)
        options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화 (일부 환경에서 필요)
        service = ChromeService(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()
    
    def fetch_seat_info(self, data):
        def save_screenshot_on_supabase(file_path):
          supabase_client.storage.from_(bucket).update(path=file_path, file=file_path)
        data_id = data['id']
        base_url = data['url']
        name = data['name']
        size_x = data['size_x']
        size_y = data['size_y']
        try:
            with self as scraper:
                scraper.driver.get(base_url)
                scraper.driver.implicitly_wait(10)
                time.sleep(1)

                scraper.driver.set_window_size(size_x, size_y)
                element = self.driver.find_element(By.ID, 'clicker_div_guide_map')
                if element:
                    # 요소 스크린샷 찍기
                    file_path = f'clicker/{data_id}.png'
                    element.screenshot(file_path)
                    save_screenshot_on_supabase(file_path)
                else:
                    print("ID가 'clicker_div_guide_map'인 요소를 찾을 수 없습니다.")
        except Exception as e:
            error_message = f'클리커 좌석 정보 스크래핑 실패: {e}의 사유로 좌석 정보를 스크래핑하지 못했습니다.'
            print(error_message)
            Slack_Notifier().fail(error_message)
            traceback.print_exc()

if __name__ == '__main__':
    datas = [{"id": 1,
             "name": "새 둥지 1열람실(2층)",
             "url": "https://clicker.gnu.ac.kr/Clicker/UserSeat/20230321132944292?DeviceName=normal",
             "size_x": "1920",
              "size_y": "700",
              },
             {
              "id": 2,
              "name": "새 둥지 2열람실(3층)",
              "url": "https://clicker.gnu.ac.kr/Clicker/UserSeat/20230321141812873?DeviceName=normal",
              "size_x": "1920",
              "size_y": "920",
             },
             {
              "id": 3,
              "name": "2층 열람실 소통줄기",
              "url": "https://clicker.gnu.ac.kr/Clicker/UserSeat/20231030135859682?DeviceName=normal",
              "size_x": "1000",
              "size_y": "1100",
             },
             {
              "id": 4,
              "name": "3층 열람실 사유잎새",
              "url": "https://clicker.gnu.ac.kr/Clicker/UserSeat/20231030140209981?DeviceName=normal",
              "size_x": "1920",
              "size_y": "1200",
             }]
    for data in datas:
        ClickerScraper(driver_path).fetch_seat_info(data)