from src.supabase_utils import supabase
import requests
from bs4 import BeautifulSoup

#response = supabase().table('it-category').select("*").execute()
#datas = response.data

datas = [{'id': 2, 'category': '공지사항', 'mi': 16376, 'bbs_id': 2206, 'created_at': '2024-03-15T08:39:15.494631+00:00', 'department': 'english'}, 
         {'id': 3, 'category': '공지사항', 'mi': 6201, 'bbs_id': 2219, 'created_at': '2024-03-15T08:39:15.494631+00:00', 'department': 'e_language'}]

for data in datas:
    category_id = data['id']
    department = data['department']
    mi = data['mi']
    bbs_id = data['bbs_id']
    base_url = f'https://www.gnu.ac.kr/{department}/na/ntt/selectNttList.do?mi={mi}&bbsId={bbs_id}'
    
    request = requests.get(base_url)
    parsed_html = BeautifulSoup(request.text, 'html.parser')
    getNums = parsed_html.find_all('b', {'class': 'btn_S btn_default'})
    print(getNums)
    

    