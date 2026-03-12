from ..models.cafeteria import Cafeteria, CafeteriaDish
from ..utils.database import get_supabase_client
from datetime import datetime
from typing import List


class CafeteriaRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def get_cafeterias(self) -> List[Cafeteria]:
        response = self.client.table('cafeteria').select('*').execute()
        raw_data = response.data or []

        return [
            Cafeteria(
                id=item['id'],
                campus_id=item['campus_id'],
                cafeteria_name_ko=item['cafeteria_name_ko'],
                mi=item['mi'],
                rest_seq=item['rest_seq'],
                type=item['type'],
                sch_sys_id=item.get('sch_sys_id'),
                form_type=item['form_type'],
                last_date=datetime.fromisoformat(
                    item['last_date']),
                thumbnail_url=item['thumbnail_url']
            )
            for item in raw_data
        ]

    def save_dishes(self, dishes: List[CafeteriaDish], cafeteria_id: int) -> None:
        if not dishes:
            return

        dish_dicts = [dish.__dict__ for dish in dishes]
        self.client.table('cafeteria_diet').insert(dish_dicts).execute()
        self.update_last_date(cafeteria_id, dishes[-1].date)

    def update_last_date(self, cafeteria_id: int, last_date: str) -> None:
        self.client.table('cafeteria').update({
            'last_date': last_date
        }).eq('id', cafeteria_id).execute()

    def delete_dishes_by_date_range(self, cafeteria_id: int, start_date: datetime, end_date: datetime) -> None:
        self.client.table('cafeteria_diet').delete().eq(
            'cafeteria_id', cafeteria_id
        ).gte('date', start_date).lte('date', end_date).execute()

    def delete_past_dishes(self, cafeteria_id: int, date: datetime) -> None:
        self.client.table('cafeteria_diet').delete().eq(
            'cafeteria_id', cafeteria_id
        ).lt('date', date).execute()
