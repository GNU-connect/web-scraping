from dataclasses import dataclass
from datetime import datetime

@dataclass
class AcademicCalendar:
    calendar_type: int
    start_date: datetime
    end_date: datetime
    content: str