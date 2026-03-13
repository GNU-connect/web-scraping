from .base import SeleniumScraper, RequestScraper
from .academic_calendar import AcademicCalendarScraper
from .cafeteria import CafeteriaScraper
from .notice import NoticeScraper
from .shuttle import ShuttleScraper

__all__ = [
    "SeleniumScraper",
    "RequestScraper",
    "AcademicCalendarScraper",
    "CafeteriaScraper",
    "NoticeScraper",
    "ShuttleScraper",
]