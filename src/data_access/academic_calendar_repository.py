from ..models.academic_calendar import AcademicCalendar
from ..utils.database import get_supabase_client
from typing import List

def insert_schedules(schedules: List[AcademicCalendar]) -> None:
    get_supabase_client().table('academic_calendar').insert(schedules).execute()

def delete_schedules() -> None:
    get_supabase_client().table('academic_calendar').delete().neq('content', 0).execute()