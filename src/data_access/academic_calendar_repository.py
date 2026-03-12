from ..models.academic_calendar import AcademicCalendar
from ..utils.database import get_supabase_client
from typing import List


class AcademicCalendarRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def insert_schedules(self, schedules: List[AcademicCalendar]) -> None:
        schedule_dicts = [
            {
                'calendar_type': s.calendar_type,
                'start_date': s.start_date.isoformat(),
                'end_date': s.end_date.isoformat(),
                'content': s.content
            }
            for s in schedules
        ]
        self.client.table('academic_calendar').insert(schedule_dicts).execute()

    def delete_schedules(self) -> None:
        self.client.table('academic_calendar').delete().neq(
            'content', 0).execute()
