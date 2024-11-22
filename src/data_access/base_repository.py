from ..utils.database import get_supabase_client
from ..models.base import College
from typing import List

COLLEGE = 'college'

def get_colleges() -> List[College]:
    try:
        response = get_supabase_client().table(COLLEGE).select('*').execute()
        raw_data = response.data

        if not raw_data:
            raise ValueError("Cafeteria 데이터를 가져오지 못했습니다.")
        
        colleges = [
            College(
                id = item['id'],
                college_ko = item['college_ko'],
                college_en = item['college_en'],
                etc_value = item['etc_value'],
                campus_id = item['campus_id']
            )
            for item in raw_data
        ]
        
        return colleges
    
    except Exception as e:
        return []