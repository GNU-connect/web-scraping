from ..utils.database import get_supabase_client
from ..models.shuttle import ShuttleTimetable

SHUTTLE_TIMETABLE = 'shuttle_timetable'


class ShuttleRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def upsert_timetable(self, timetable: ShuttleTimetable) -> None:
        self.client.table(SHUTTLE_TIMETABLE).upsert(
            {
                'route_name': timetable.route_name,
                'timetable': timetable.timetable,
                'updated_at': timetable.updated_at.isoformat(),
                'last_success_at': timetable.last_success_at.isoformat(),
            },
            on_conflict='route_name',
        ).execute()
