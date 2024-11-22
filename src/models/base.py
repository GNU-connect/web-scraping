from dataclasses import dataclass

@dataclass
class College:
    id: int
    college_ko: str
    college_en: str
    etc_value: bool
    campus_id: int