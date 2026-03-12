from .base import RequestScraper
from bs4 import BeautifulSoup
from ..models.cafeteria import Cafeteria, CafeteriaDish, DishSlotContext
from ..data_access.cafeteria_repository import CafeteriaRepository
from typing import List, Any
from datetime import datetime


class CafeteriaScraper(RequestScraper):
    DISH_TYPE_LIST = ['주식', '국류', '찬류', '후식']
    DAY_LIST = ['월', '화', '수', '목', '금', '토', '일']
    TIME_LIST = ['아침', '점심', '저녁']

    def __init__(self, cafeteria: Cafeteria, repository: CafeteriaRepository = None):
        super().__init__(base_url=None)
        self.cafeteria = cafeteria
        self.repository = repository or CafeteriaRepository()
        self.base_url = self._get_base_url()

    def _get_base_url(self) -> str:
        cafeteria = self.cafeteria
        base_url = f'https://www.gnu.ac.kr/{cafeteria.type}/ad/fm/foodmenu/selectFoodMenuView.do?restSeq={cafeteria.rest_seq}&mi={cafeteria.mi}'
        if cafeteria.sch_sys_id:
            base_url += f'&schSysId={cafeteria.sch_sys_id}'
        return base_url

    def _parse_menu_data(self, parsed_html: BeautifulSoup) -> tuple[datetime, datetime, List[CafeteriaDish]]:
        thead_element = parsed_html.find('thead')
        tbody_element = parsed_html.find('tbody')

        dish_headers = thead_element.find_all('th')[1:]
        date_list = [datetime.strptime(header.text.strip().split(' ')[1], '%Y-%m-%d')
                     for header in dish_headers]
        start_date = min(date_list)
        end_date = max(date_list)

        dish_time_htmls = tbody_element.find_all('tr')
        result = []

        max_slots = (
            len(self.DISH_TYPE_LIST)
            if self.cafeteria.form_type == 2
            else len(self.TIME_LIST)
        )
        repeat_number = min(len(dish_time_htmls), max_slots)

        for t in range(repeat_number):
            dishes = self._process_time_slot(t, dish_time_htmls, date_list)
            result.extend(dishes)

        return (start_date, end_date, result)

    def _get_meal_time(self, index: int) -> str:
        if self.cafeteria.cafeteria_name_ko == '교육문화식당' or self.cafeteria.form_type == 2:
            return '점심'
        return self.TIME_LIST[index]

    def _process_day_slot(self, dish_day_html: Any, context: DishSlotContext) -> List[CafeteriaDish]:
        dishes = []
        categories = dish_day_html.find_all('div')
        current_category = None

        for category in categories:
            category_header = category.find('p', class_='mgt15')
            if category_header:
                current_category = category_header.text.strip()

            menu_items = category.find('p', class_='')
            if not menu_items or not menu_items.get_text():
                continue

            menu_list = menu_items.get_text(separator='<br>').split('<br>')
            for menu_item in menu_list:
                if not menu_item.strip():
                    continue

                dishes.append(CafeteriaDish(
                    cafeteria_id=self.cafeteria.id,
                    date=context.date.isoformat(),
                    day=context.day,
                    dish_type=context.dish_type,
                    dish_category=current_category,
                    time=context.meal_time,
                    dish_name=menu_item
                ))

        return dishes

    def _process_time_slot(self, time_index: int, dish_time_htmls: List[Any], date_list: List[datetime]) -> List[CafeteriaDish]:
        dish_type = self.DISH_TYPE_LIST[time_index] if self.cafeteria.form_type == 2 else None
        meal_time = self._get_meal_time(time_index)

        dish_day_htmls = dish_time_htmls[time_index].find_all('td')
        dishes = []

        for day_index, day in enumerate(self.DAY_LIST):
            if day_index >= len(dish_day_htmls):
                continue

            context = DishSlotContext(
                date=date_list[day_index], day=day, meal_time=meal_time, dish_type=dish_type)
            dishes.extend(self._process_day_slot(
                dish_day_htmls[day_index], context))

        return dishes

    def get_scraper_name(self):
        return f"식단 메뉴 ({self.cafeteria.cafeteria_name_ko})"

    def scrape_data(self, save_data: bool = False):
        try:
            with self:
                parsed_html = self.parsed_html(self.base_url)
                if parsed_html is None:
                    raise ValueError(f'식단 페이지 요청 실패: {self.base_url}')

                start_date, end_date, dishes = self._parse_menu_data(
                    parsed_html)

                if dishes and save_data:
                    self.repository.delete_dishes_by_date_range(
                        self.cafeteria.id, start_date, end_date)
                    self.repository.save_dishes(dishes, self.cafeteria.id)
                print(f'[교내 식당] {self.cafeteria.campus_id}번 캠퍼스 {self.cafeteria.cafeteria_name_ko}의 '
                      f'새로운 식단 데이터 {len(dishes)}개를 스크래핑했습니다.')

        except Exception as e:
            context_message = f"{self.cafeteria.campus_id}번 캠퍼스 {self.cafeteria.cafeteria_name_ko} 식단 데이터 조회 실패"
            self.notify_failure(e, context_message)
