from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Cafeteria:
    id: int
    campus_id: int
    cafeteria_name_ko: str
    mi: int
    rest_seq: int
    type: str
    sch_sys_id: Optional[int]
    form_type: int
    last_date: datetime
    thumbnail_url: str

@dataclass
class CafeteriaDish:
    cafeteria_id: int
    date: str
    day: str
    dish_type: Optional[str]
    dish_category: Optional[str]
    time: str
    dish_name: str