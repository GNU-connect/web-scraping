from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup

#response = supabase().table('it-category').select("*").execute()
#datas = response.data

datas = [{
    'id': 2, 'category': '공지사항', 'mi': 16376, 'bbs_id': 2206, 'created_at': '2024-03-15T08:39:15.494631+00:00', 'department': 'english', 'last_board_id': 0}, 
         {'id': 3, 'category': '공지사항', 'mi': 6201, 'bbs_id': 2219, 'created_at': '2024-03-15T08:39:15.494631+00:00', 'department': 'e_language', 'last_board_id': 0}]

notice_objects = []

for data in datas:
    category_id, department, mi, bbs_id, last_board_id = data['id'], data['department'], data['mi'], data['bbs_id'], data['last_board_id']
    base_url = f'https://www.gnu.ac.kr/{department}/na/ntt/'
    department_board_url = f'{base_url}selectNttList.do?mi={mi}&bbsId={bbs_id}'

    request = requests.get(department_board_url)
    parsed_html = BeautifulSoup(request.text, 'html.parser')
    
    # 공지사항 가져오기
    new_notice_htmls = [tag.find_parent('tr') for tag in parsed_html.find_all('td', class_='BD_tm_none') if tag.text.strip().isdigit() and int(tag.text.strip()) > last_board_id] # 최신 공지사항만 가져오기
    for new_notice_html in new_notice_htmls:
        notice_id = new_notice_html.find('td', class_='BD_tm_none').text.strip()
        title = new_notice_html.find('a').contents[0].strip()
        link = new_notice_html.find('a')['href']
        ntt_sn = new_notice_html.find('a', class_='nttInfoBtn')['data-id']
        thumbnail_url = f'{base_url}selectNttInfo.do?mi={mi}&nttSn={ntt_sn}&bbsId={bbs_id}'
    
        notice_object = {
            'department': department,
            'category_id': category_id,
            'title': title,
            'ntt_sn': ntt_sn,
            'notice_id': notice_id,
        }
        
        notice_objects.append(notice_object)

response = supabase().table('inmun').insert(notice_objects).execute()

# 결과 확인
if response.error:
    print('Error:', response.error)
else:
    print('Insertion successful:', response.data)
    

    

    