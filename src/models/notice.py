from dataclasses import dataclass
from datetime import datetime

@dataclass
class NoticeCategory:
    id: int
    category: str
    mi: int
    bbs_id: int
    department_id: int
    last_ntt_sn: int
    department_en: str
    department_ko: str

@dataclass
class Notice:
    department_id: int
    category_id: int
    title: str
    ntt_sn: int
    created_at: datetime