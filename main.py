from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup

# 전역 변수
max_num_notices = 5
college = 'inmun'

response = supabase().table(f'{college}-category').select("*").execute()
datas = response.data

# datas = [{
#     'id': 40, 'category': '공지사항', 'mi': 10518, 'bbs_id': 1458, 'updated_at': '2024-03-15T08:39:15.494631+00:00', 'department': 'sophia', 'last_ntt_sn': 2229329}]

for data in datas:
    category_id, department, mi, bbs_id, last_ntt_sn = data['id'], data['department'], data['mi'], data['bbs_id'], data['last_ntt_sn']
    try:
      notice_objects = []
      base_url = f'https://www.gnu.ac.kr/{department}/na/ntt/'
      department_board_url = f'{base_url}selectNttList.do?mi={mi}&bbsId={bbs_id}'

      request = requests.get(department_board_url)
      parsed_html = BeautifulSoup(request.text, 'html.parser')
      
      tbody_element = parsed_html.find('tbody')
      new_notice_htmls = tbody_element.find_all('tr')

      for new_notice_html in new_notice_htmls:
          ntt_sn = new_notice_html.find('a', class_='nttInfoBtn')['data-id']
          # ntt_sn가 last_ntt_sn보다 작거나 같으면 break
          if int(ntt_sn) <= last_ntt_sn:
              break
          notice_id = new_notice_html.find('td', class_='BD_tm_none').text.strip()
          title = new_notice_html.find('a').contents[0].strip()
          notice_object = {
              'department': department,
              'category_id': category_id,
              'title': title,
              'ntt_sn': int(ntt_sn),
          }
          notice_objects.append(notice_object)
      
      # ntt_sn 기준으로 내림차순 뒤, 5개만 가져온다.
      result = sorted(notice_objects, key=lambda x: x['ntt_sn'], reverse=True)[:5]

      # 공지사항 카테고리의 last_ntt_sn을 업데이트한다.
      #supabase().table(f'{college}-category').update({'last_ntt_sn': int(result[0]['ntt_sn'])}).eq('id', category_id).execute()

      # 해당 학과 카테고리의 공지사항을 조회하여 개수를 확인한다.
      existing_notices = supabase().from_(f'{college}-notice').select('id, ntt_sn').eq('category_id', category_id).execute().data
      
      # 만약 해당 학과 카테고리 테이블에 공지사항의 자리가 충분하다면, 새로운 공지사항을 삽입한다.
      if len(result) <= max_num_notices - len(existing_notices):
          supabase().table(f'{college}-notice').insert(result).execute()
      # 충분하지 않다면, 오래된 공지사항의 자리부터 새로운 공지사항으로 교체한다.
      else:
          for newest_notice in result:
            oldest_notice = min(existing_notices, key=lambda x: x['ntt_sn'])
            oldest_notice_id = oldest_notice['id']
            supabase().table(f'{college}-notice').update(newest_notice).eq('id', oldest_notice_id).execute()
         
    except Exception as e:
      print(category_id, department, mi, bbs_id, e)
      continue
    

    

    