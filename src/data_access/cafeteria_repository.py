from ..models.cafeteria import Cafeteria
from ..utils.database import get_supabase_client
from datetime import datetime

def get_cafeterias() -> list[Cafeteria]:
    try:
        # Supabase에서 데이터를 가져옴
        response = get_supabase_client().table('cafeteria').select('*').execute()
        raw_data = response.data

        if not raw_data:
            raise ValueError("Cafeteria 데이터를 가져오지 못했습니다.")

        # 데이터를 Cafeteria 객체로 매핑
        cafeterias = [
            Cafeteria(
                id=item['id'],
                campus_id=item['campus_id'],
                cafeteria_name_ko=item['cafeteria_name_ko'],
                mi=item['mi'],
                rest_seq=item['rest_seq'],
                type=item['type'],
                sch_sys_id=item.get('sch_sys_id'),
                form_type=item['form_type'],
                last_date=datetime.fromisoformat(item['last_date']),
                thumbnail_url=item['thumbnail_url']
            )
            for item in raw_data
        ]

        return cafeterias
    except Exception as e:
        print(f"Error fetching cafeterias: {e}")
        return []