from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup
import traceback
from datetime import datetime

max_num_notices = 5 # 스크래핑 할 공지사항 개수 (변경 X)

class Scraper:
    def __init__(self, college):
        self.college = college

    def scrape_notice_data(self):
        # 학과별 카테고리 데이터 가져오기
        datas = self.get_category_data(self.college)
        if datas is None:
          print(f'{self.college}의 카테고리 데이터를 가져오는데 실패했습니다.')
          return
        
        # 학과 카테고리별 공지사항 스크래핑
        for data in datas:
          category_id = data['id']
          department_id = data['department_id']
          department_en = data['department']['department_en']
          mi = data['mi']
          bbs_id = data['bbs_id']
          last_ntt_sn = data['last_ntt_sn']

          notice_objects = []
          base_url = f'https://www.gnu.ac.kr/{department_en}/na/ntt/'
          department_board_url = f'{base_url}selectNttList.do?mi={mi}&bbsId={bbs_id}'

          try:
            request = requests.get(department_board_url)
            parsed_html = BeautifulSoup(request.text, 'html.parser')

            tbody_element = parsed_html.find('tbody')
            new_notice_htmls = tbody_element.find_all('tr')

            # 새로운 공지사항 확인
            for new_notice_html in new_notice_htmls:
                ntt_sn = new_notice_html.find('a', class_='nttInfoBtn')['data-id']
                date = new_notice_html.find_all('td')[3].text.strip()
                date = datetime.strptime(date, '%Y.%m.%d')
                if int(ntt_sn) <= last_ntt_sn:
                    break
                # 너무 오래된 공지사항은 스크래핑하지 않음
                if (datetime.now() - date).days > 30:
                   break
                title = new_notice_html.find('a').contents[0].strip()
                notice_object = {
                    'department_id': department_id,
                    'category_id': category_id,
                    'title': title,
                    'ntt_sn': int(ntt_sn),
                    'created_at': date.isoformat(),
                }
                notice_objects.append(notice_object)
            
            if len(notice_objects) == 0:
                continue
            
            # 최신 공지사항 5개만 가져오기
            result = sorted(notice_objects, key=lambda x: x['ntt_sn'], reverse=True)[:5]

            # 공지사항 삽입(또는 교체)
            existing_notices = self.get_existing_notices(category_id)
            if len(result) <= max_num_notices - len(existing_notices):
                self.insert_notices(result)
            else:
                for i in range(len(result)):
                    newest_notice = result[i]
                    oldest_notice = existing_notices[i]
                    self.update_notice(newest_notice, oldest_notice['id'])
            self.update_category_last_ntt_sn(category_id, result[0]['ntt_sn'])
            print(f"{department_en}의 {category_id}번 카테고리의 새로운 공지사항 {len(result)}개를 스크래핑했습니다.")

          except Exception as e:
            tb = e.__traceback__
            tb_info = traceback.extract_tb(tb)
            for line in tb_info:
                filename, line_no, func_name, source_code = line
                print(f"{filename}:{line_no} 에서 {e.__class__.__name__} 발생")
            print(f'스크래핑 실패: {department_en}의 {category_id}번 카테고리를 {e} 의 사유로 실패했습니다.')
            continue
    
    def get_category_data(self, college):
        try:
          datas = supabase().table(f'{college}-category').select(f'*, department(department_en)').execute().data
          return datas
        except Exception as e:
          return None

    def update_category_last_ntt_sn(self, category_id, last_ntt_sn):
        supabase().table(f'{self.college}-category').update({'last_ntt_sn': int(last_ntt_sn)}).eq('id', category_id).execute()

    def get_existing_notices(self, category_id):
        return supabase().from_(f'{self.college}-notice').select('id, ntt_sn').eq('category_id', category_id).execute().data

    def insert_notices(self, notices):
        supabase().table(f'{self.college}-notice').insert(notices).execute()

    def update_notice(self, notice, notice_id):
        supabase().table(f'{self.college}-notice').update(notice).eq('id', notice_id).execute()
