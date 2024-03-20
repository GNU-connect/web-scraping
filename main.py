from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup

response = supabase().table('inmun-category').select("*").execute()
datas = response.data

# datas = [{
#     'id': 11, 'category': '공지사항', 'mi': 3286, 'bbs_id': 1463, 'created_at': '2024-03-15T08:39:15.494631+00:00', 'department': 'russia', 'last_board_id': 0}]

for data in datas:
    category_id, department, mi, bbs_id, last_board_id = data['id'], data['department'], data['mi'], data['bbs_id'], data['last_board_id']
    try:
      notice_objects = []
      base_url = f'https://www.gnu.ac.kr/{department}/na/ntt/'
      department_board_url = f'{base_url}selectNttList.do?mi={mi}&bbsId={bbs_id}'

      request = requests.get(department_board_url)
      parsed_html = BeautifulSoup(request.text, 'html.parser')
      
      # 게시판 id가 '공지'가 아닌 것들만 가져옴
      new_notice_htmls = []
      tbody_element = parsed_html.find('tbody')
      tr_count = len(tbody_element.find_all('tr'))
      tags = parsed_html.find_all('td', class_='BD_tm_none')
      # 예외 처리 (조회수 등에 의해 한 행에 tr이 두개씩 생기는 경우가 있음)
      if len(tags) >= tr_count:
         tags = tags[::2]
      for tag in tags:
          if tag.text.strip().isdigit() and int(tag.text.strip()) > last_board_id:
              new_notice_htmls.append(tag.find_parent('tr'))
      for i in range(5):
          if i >= len(new_notice_htmls):
              break
          new_notice_html = new_notice_htmls[i]
          notice_id = new_notice_html.find('td', class_='BD_tm_none').text.strip()
          title = new_notice_html.find('a').contents[0].strip()
          ntt_sn = new_notice_html.find('a', class_='nttInfoBtn')['data-id']
      
          notice_object = {
              'department': department,
              'category_id': category_id,
              'title': title,
              'ntt_sn': ntt_sn,
              'notice_id': notice_id,
          }
          
          notice_objects.append(notice_object)
      response = supabase().table('inmun').insert(notice_objects).execute()
    except Exception as e:
      print(category_id, department, mi, bbs_id, last_board_id, e)
      continue
    

    

    