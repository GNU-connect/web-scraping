from ..utils.database import get_supabase_client
from typing import List
from ..models.notice import NoticeCategory, Notice

NOTICE = 'notice'
CATEGORY = 'notice_category'


def get_notice_categories() -> List[NoticeCategory]:
    try:
        response = get_supabase_client().table(CATEGORY).select(
            f'*, department(department_en, department_ko)').execute()
        raw_data = response.data

        categories = [
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

        return categories

    except Exception:
        return []


def get_category_notices(category_id: int) -> List[Notice]:
    """기존 공지사항을 가져옵니다."""
    return get_supabase_client().table(NOTICE).select('*').eq('category_id', category_id).execute().data


def insert_notices(notices: List[Notice]) -> None:
    """새 공지사항을 삽입합니다."""
    if notices:
        get_supabase_client().table(NOTICE) \
            .insert([vars(notice) for notice in notices]) \
            .execute()


def update_notice(notice: Notice, notice_id: int) -> None:
    """기존 공지사항을 업데이트합니다."""
    get_supabase_client().table(NOTICE) \
        .update(vars(notice)) \
        .eq('id', notice_id) \
        .execute()


def update_category_last_ntt_sn(category_id: int, last_ntt_sn: int) -> None:
    """카테고리의 마지막 공지사항 번호를 업데이트합니다."""
    get_supabase_client().table(CATEGORY) \
        .update({'last_ntt_sn': last_ntt_sn}) \
        .eq('id', category_id) \
        .execute()
