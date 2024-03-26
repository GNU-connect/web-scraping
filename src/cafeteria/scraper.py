from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup
import traceback
from datetime import datetime

class Cafeteria_Scraper:
    def scrape_cafeteria_dish_data(self):
        datas = self.get_cafeteria_data()
        if datas is None:
          print('식단 데이터 조회 실패: 식단 데이터를 가져오는데 실패했습니다.')
          return
        
        # 식단 데이터 스크래핑
        for data in datas:
          campus_id = data['campus_id']
          cafeteria_id = data['id']
          cafeteria_name_ko = data['cafeteria_name_ko']
          mi = data['mi']
          rest_seq = data['rest_seq']
          type = data['type']
          sch_sys_id = data['sch_sys_id']
          only_lunch = data['only_lunch']

          notice_objects = []
          base_url = f'https://www.gnu.ac.kr/{type}/ad/fm/foodmenu/selectFoodMenuView.do?restSeq={rest_seq}&mi={mi}'
          if sch_sys_id != None:
            base_url += f'&schSysId={sch_sys_id}'

          try:
            request = requests.get(base_url)
            parsed_html = BeautifulSoup(request.text, 'html.parser')
            
            thead_element = parsed_html.find('thead')
            tbody_element = parsed_html.find('tbody')

            dish_headers = thead_element.find_all('th')[1:]

            date_list = [datetime.strptime(dish_header.text.strip().split(' ')[1], '%Y-%m-%d') for dish_header in dish_headers]
            day_list = ['월', '화', '수', '목', '금', '토', '일']
            time_list = ['아침', '점심', '저녁']

            # TODO: 오래된 식단 데이터는 스크래핑하지 않도록 조건문 추가
            
            dish_time_htmls = tbody_element.find_all('tr')

            # 점심 메뉴만 제공해주는 식당일 경우 (ex. 교직원 식당)
            if only_lunch:
               pass
            else:
              time_idx = 0
              # 행(시간) 단위로 식단 데이터 처리
              for t in range(len(dish_time_htmls) if len(dish_time_htmls) < len(time_list) else len(time_list)):
                dish_time_html = dish_time_htmls[t]
                time = time_list[t]
                time_idx += 1
                dish_day_htmls = dish_time_html.find_all('td')
                # 열(요일) 단위로 식단 데이터 처리
                for d in range(len(day_list)):
                   dish_day_html = dish_day_htmls[d]
                   date = date_list[d]
                   day = day_list[d]
                   course = None
                   dish_type = None
                   categories = dish_day_html.find_all('div')
                   for category in categories:
                      # 카테고리 헤더 처리
                      category_header = category.find('p', class_='mgt15')
                      if category_header is not None:
                        category_header = category_header.text.strip().split('/')
                        if len(category_header) == 2:
                          course = category_header[0]
                          dish_type = category_header[1]
                        else:
                          dish_type = category_header[0]
                      # 메뉴 처리
                      dishes = category.find('p', class_='')
                      if dishes is not None:
                        dishes = dishes.get_text(separator='<br>').split('<br>')
                        # TODO: 식단 데이터 저장
              
              # 남은 time 식단 데이터 처리
              while time_idx < len(dish_time_htmls):
                time_idx += 1
                

          except Exception as e:
            print(f'식단 데이터 조회 실패: {campus_id}번 캠퍼스의 {cafeteria_name_ko} 식단 데이터를 가져오는데 실패했습니다.')
            traceback.print_exc()
            return
    
    def get_cafeteria_data(self):
        try:
          datas = supabase().table('cafeteria').select('*').execute().data
          return datas
        except Exception as e:
          return None