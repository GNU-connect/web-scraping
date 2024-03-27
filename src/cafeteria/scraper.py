from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup
import traceback
from datetime import datetime, timedelta

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
          form_type = data['form_type']
          last_date = data['last_date']
          last_date = datetime.fromisoformat(last_date)

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
            dish_type_list = ['주식', '국류', '찬류', '후식']
            day_list = ['월', '화', '수', '목', '금', '토', '일']
            time_list = ['아침', '점심', '저녁']
            
            dish_time_htmls = tbody_element.find_all('tr')

            result = []
            # 행(시간) 단위로 식단 데이터 처리
            for t in range(len(dish_time_htmls) if len(dish_time_htmls) < len(time_list) else len(time_list)):
              dish_type = dish_type = dish_type_list[t] if form_type == 2 else None
              dish_time_html = dish_time_htmls[t]
              # 점심 메뉴만 제공해주는 식당일 경우 (ex. 교직원 식당)
              time = '점심' if cafeteria_name_ko == '교육문화1층식당' or form_type == 2 else time_list[t]
              dish_day_htmls = dish_time_html.find_all('td')
              # 열(요일) 단위로 식단 데이터 처리
              for d in range(len(day_list)):
                  dish_object = {}
                  dish_day_html = dish_day_htmls[d]
                  date = date_list[d]
                  if date.replace(tzinfo=last_date.tzinfo) <= last_date:
                    continue
                  day = day_list[d]
                  dish_category = None
                  categories = dish_day_html.find_all('div')
                  for category in categories:
                    # 카테고리 헤더 처리
                    category_header = category.find('p', class_='mgt15')
                    if category_header is not None:
                      dish_category = category_header.text.strip()
                    # 메뉴 처리
                    dishes = category.find('p', class_='')
                    if dishes is not None:
                      dishes = dishes.get_text(separator='<br>').split('<br>')
                      is_set_menu = False  # 변수를 설정하여 (세트메뉴)가 발견되었는지 추적합니다.
                      tmp_dish = None # tmp 변수
                      for dish_idx in range(len(dishes)):
                        dish = dishes[dish_idx]
                        if dish == ' ' or dish == '':
                          continue
                        # 중앙식당 점심과 저녁은 임의로 dish_category을 붙여줌
                        if cafeteria_name_ko == '중앙1식당' and (time == '점심' or time == '저녁'):
                          if dish == '(세트메뉴)':
                            is_set_menu = True
                            continue
                          if not is_set_menu:
                            dish_categorys = ['뚝빼기/비빔밥', '양식']
                            dish_category = dish_categorys[dish_idx]
                          else:
                            dish_category = '세트메뉴'
                        # 칠암 제2분관 식당의 경우, 메뉴가 '/'로 나뉘어져 있음
                        elif cafeteria_name_ko == '칠암 제2분관 식당' and time == '아침':
                          if dish.startswith('★'):
                            dish_category = dish[1:]
                            continue
                          elif '(' in dish:
                            tmp_dish = dish[1:-1]
                            continue
                          elif dish.startswith('-'):
                            if dish_category.startswith('샐러드'):
                              dish = (dish.lstrip('-') + " " + tmp_dish).strip()
                            else:
                              dish = tmp_dish
                        elif cafeteria_name_ko == '학생식당' and time == '아침' and campus_id == 2:
                          if "천원의 아침밥 사업 시행에 따라" in dish:
                            break
                          elif dish == "(천원의 아침밥)":
                            dish_category = "천원의아침밥"
                            continue
                        
                        # TODO: 식단 데이터 저장
                        dish_object = {
                          'cafeteria_id': cafeteria_id,
                          'date': date.isoformat(),
                          'day': day,
                          'dish_type': dish_type,
                          'dish_category': dish_category,
                          'time': time,
                          'dish_name': dish
                        }
                        print(dish_object)
                        result.append(dish_object)
            if len(result) > 0:
              # 식단 데이터 삽입
              self.insert_dishes(result)
              # last_date 업데이트
              self.update_cafeteria_last_date(cafeteria_id, result[-1]['date'])
                
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
    
    def delete_oldest_dishes(self):
      now_date = datetime.now() - timedelta(days=1)
      supabase().table('cafeteria-diet').delete().lt('date', now_date).execute()
    
    def insert_dishes(self, dishes):
      supabase().table('cafeteria-diet').insert(dishes).execute()
    
    def update_cafeteria_last_date(self, cafeteria_id, last_date):
      supabase().table('cafeteria').update({'last_date': last_date}).eq('id', cafeteria_id).execute()