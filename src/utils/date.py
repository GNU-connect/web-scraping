from datetime import datetime

def get_midnight(date: datetime) -> datetime:
    """오늘 자정 시각을 반환"""
    return datetime.combine(date, date.min.time())