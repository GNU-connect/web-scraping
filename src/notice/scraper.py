from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup
import traceback
from datetime import datetime
from src.slack_utils import Slack_Notifier

max_num_notices = 5 # 스크래핑 할 공지사항 개수 (변경 X)

class Notice_Scraper:
    def __init__(self, college):
        self.college = college

    def scrape_notice_data(self):
        # 학과별 카테고리 데이터 가져오기
        datas = self.get_category_data(self.college)
        if datas is None:
          print(f'학과 카테고리 조회 실패: {self.college}의 카테고리 데이터를 가져오는데 실패했습니다.')
          return
        
        # 학과 카테고리별 공지사항 스크래핑
        for data in datas:
          category_id = data['id']
          category = data['category']
          department_id = data['department_id']
          department_en = data['department']['department_en']
          department_ko = data['department']['department_ko']
          mi = data['mi']
          bbs_id = data['bbs_id']
          last_ntt_sn = data['last_ntt_sn']

          notice_objects = []
          base_url = f'https://www.gnu.ac.kr/{department_en}/na/ntt/'
          department_board_url = f'{base_url}selectNttList.do?mi={mi}&bbsId={bbs_id}'

          try:
            request = requests.get(department_board_url)
            parsed_html = BeautifulSoup(request.text, 'html.parser')

            thead_element = parsed_html.find('thead')
            tbody_element = parsed_html.find('tbody')

            notice_headers = thead_element.find_all('th')
            new_notice_htmls = tbody_element.find_all('tr')

            # 테이블 헤더 전처리
            for i in range(len(notice_headers)):
                notice_headers[i] = notice_headers[i].text.strip()
            
            # 새로운 공지사항 확인
            for new_notice_html in new_notice_htmls:
                ntt_sn = new_notice_html.find('a', class_='nttInfoBtn')['data-id']
                date_idx = notice_headers.index('등록일')
                date = new_notice_html.find_all('td')[date_idx].text.strip()
                date = datetime.strptime(date, '%Y.%m.%d')
                # 이전에 스크래핑한 공지사항은 스크래핑하지 않음
                if int(ntt_sn) <= last_ntt_sn:
                    continue
                # 너무 오래된 공지사항은 스크래핑하지 않음
                if (datetime.now() - date).days > 30:
                   continue
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
            empty_space = max_num_notices - len(existing_notices)
            self.insert_notices(result[:empty_space])
            
            for i in range(len(result[empty_space:])):
                newest_notice = result[empty_space:][i]
                oldest_notice = existing_notices[i]
                self.update_notice(newest_notice, oldest_notice['id'])
            self.update_category_last_ntt_sn(category_id, result[0]['ntt_sn'])
            print(f"[공지사항] {department_ko}의 {category} 카테고리의 새로운 공지사항 {len(result)}개를 스크래핑했습니다.")

          except Exception as e:
            print(f'[공지사항] 공지사항 데이터 조회 실패: {department_ko}의 {category} 카테고리를 {e} 의 사유로 실패했습니다.')
            print(f'[공지사항] 해당 학과 공지사항 URL: {department_board_url}')
            Slack_Notifier().fail(f'공지사항 데이터 조회 실패: {department_ko}의 {category} 카테고리를 {e} 의 사유로 실패했습니다. \n \
                                  해당 학과 공지사항 URL: {department_board_url}')
            traceback.print_exc()
            continue
    
    def get_category_data(self, college):
        try:
          datas = supabase().table(f'{college}-category').select(f'*, department(department_en, department_ko)').execute().data
          return datas
        except Exception as e:
          return None

    def update_category_last_ntt_sn(self, category_id, last_ntt_sn):
        supabase().table(f'{self.college}-category').update({'last_ntt_sn': int(last_ntt_sn)}).eq('id', category_id).execute()

    def get_existing_notices(self, category_id):
        return supabase().from_(f'{self.college}-notice').select('id, ntt_sn').eq('category_id', category_id).order('ntt_sn', desc=False).execute().data

    def insert_notices(self, notices):
        supabase().table(f'{self.college}-notice').insert(notices).execute()

    def update_notice(self, notice, notice_id):
        supabase().table(f'{self.college}-notice').update(notice).eq('id', notice_id).execute()
