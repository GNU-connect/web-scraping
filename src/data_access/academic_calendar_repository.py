from ..models.academic_calendar import AcademicCalendar
from ..utils.database import get_supabase_client
from typing import List


class AcademicCalendarRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def insert_schedules(self, schedules: List[AcademicCalendar]) -> None:
        self.client.table('academic_calendar').insert(schedules).execute()

    def delete_schedules(self) -> None:
        self.client.table('academic_calendar').delete().neq('content', 0).execute()
