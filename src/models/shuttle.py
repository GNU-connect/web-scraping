from dataclasses import dataclass
from datetime import datetime


@dataclass
class ShuttleTimetable:
    route_name: str
    timetable: dict
    updated_at: datetime
