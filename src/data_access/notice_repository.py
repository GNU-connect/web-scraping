from ..utils.database import get_supabase_client
from typing import List
from ..models.notice import NoticeCategory, Notice

NOTICE = 'notice'
CATEGORY = 'notice_category'


class NoticeRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def get_notice_categories(self) -> List[NoticeCategory]:
        try:
            response = self.client.table(CATEGORY).select(
                '*, department(department_en, department_ko)').execute()
            raw_data = response.data

            return [
                NoticeCategory(
                    id=item['id'],
                    category=item['category'],
                    mi=item['mi'],
                    bbs_id=item['bbs_id'],
                    department_id=item['department_id'],
                    last_ntt_sn=item['last_ntt_sn'],
                    department_en=item['department']['department_en'],
                    department_ko=item['department']['department_ko']
                )
                for item in raw_data
            ]
        except Exception:
            return []

    def get_category_notices(self, category_id: int) -> List[Notice]:
        return self.client.table(NOTICE).select('*').eq('category_id', category_id).execute().data

    def insert_notices(self, notices: List[Notice]) -> None:
        if notices:
            self.client.table(NOTICE) \
                .insert([vars(notice) for notice in notices]) \
                .execute()

    def update_notice(self, notice: Notice, notice_id: int) -> None:
        self.client.table(NOTICE) \
            .update(vars(notice)) \
            .eq('id', notice_id) \
            .execute()

    def update_category_last_ntt_sn(self, category_id: int, last_ntt_sn: int) -> None:
        self.client.table(CATEGORY) \
            .update({'last_ntt_sn': last_ntt_sn}) \
            .eq('id', category_id) \
            .execute()
