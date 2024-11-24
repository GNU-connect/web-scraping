from ..models.cafeteria import Cafeteria, CafeteriaDish
from ..utils.database import get_supabase_client
from datetime import datetime
from typing import List

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
        return []

def save_dishes(dishes: List[CafeteriaDish], cafeteria_id: int) -> None:
        """메뉴 데이터 저장"""
        dish_dicts = [dish.__dict__ for dish in dishes]
        get_supabase_client().table('cafeteria_diet').insert(dish_dicts).execute()
        update_last_date(cafeteria_id, dishes[-1].date)

def update_last_date(cafeteria_id: int, last_date: str) -> None:
    """마지막 날짜 업데이트"""
    get_supabase_client().table('cafeteria').update({
        'last_date': last_date
    }).eq('id', cafeteria_id).execute()

def delete_dishes_by_date_range(cafeteria_id: int, start_date: datetime, end_date: datetime) -> None:
    """기간에 해당하는 데이터 삭제"""
    get_supabase_client().table('cafeteria_diet').delete().eq('cafeteria_id', cafeteria_id).gte('date', start_date).lte('date', end_date).execute()

def delete_past_dishes(cafeteria_id: int, date: datetime) -> None:
    """과거 데이터 삭제"""
    get_supabase_client().table('cafeteria_diet').delete().eq('cafeteria_id', cafeteria_id).lt('date', date).execute()