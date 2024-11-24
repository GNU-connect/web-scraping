from ..utils.date import get_midnight
from .base import SeleniumScraper
from bs4 import BeautifulSoup
from ..models.cafeteria import Cafeteria, CafeteriaDish
from typing import List, Any, Optional
from datetime import datetime, timedelta
from ..data_access.cafeteria_repository import delete_dishes_by_date_range, delete_past_dishes, save_dishes

class CafeteriaScraper(SeleniumScraper):
    DISH_TYPE_LIST = ['주식', '국류', '찬류', '후식']
    DAY_LIST = ['월', '화', '수', '목', '금', '토', '일']
    TIME_LIST = ['아침', '점심', '저녁']
    
    def __init__(self, cafeteria: list[Cafeteria]):
        super().__init__(base_url=None)
        self.cafeteria = cafeteria
        self.base_url = self._get_base_url(cafeteria.rest_seq, cafeteria.mi, cafeteria.sch_sys_id, cafeteria.type)
        
    def _get_base_url(self, rest_seq, mi, sch_sys_id, type) -> str:
        base_url = f'https://www.gnu.ac.kr/{type}/ad/fm/foodmenu/selectFoodMenuView.do?restSeq={rest_seq}&mi={mi}'
        if sch_sys_id:
            base_url += f'&schSysId={sch_sys_id}'
        return base_url
    
    def _parse_menu_data(self, parsed_html: BeautifulSoup) -> tuple[datetime, datetime, List[CafeteriaDish]]:
        """메뉴 데이터 파싱"""
        thead_element = parsed_html.find('thead')
        tbody_element = parsed_html.find('tbody')
        
        dish_headers = thead_element.find_all('th')[1:]
        date_list = [datetime.strptime(header.text.strip().split(' ')[1], '%Y-%m-%d') 
                    for header in dish_headers]
        tomorrow = get_midnight(datetime.now()) + timedelta(days=1)
        start_date = max(min(date_list), get_midnight(tomorrow))
        end_date = max(date_list)
        filtered_date_list = [date for date in date_list if start_date <= date <= end_date]
        
        dish_time_htmls = tbody_element.find_all('tr')
        result = []
        
        repeat_number = (len(self.DISH_TYPE_LIST) if self.cafeteria.form_type == 2
                        else min(len(dish_time_htmls), len(self.TIME_LIST)))

        for t in range(repeat_number):
            dishes = self._process_time_slot(t, filtered_date_list, dish_time_htmls)
            result.extend(dishes)
            
        return (start_date, end_date, result)

    def _get_time_for_cafeteria(self, index: int) -> str:
        """식당별 시간 결정"""
        if self.cafeteria.cafeteria_name_ko == '교육문화식당' or self.cafeteria.form_type == 2:
            return '점심'
        return self.TIME_LIST[index]
    
    def _process_special_cases(self, dish: str, dish_category: Optional[str], time: str) -> tuple[Optional[str], Optional[str]]:
        """특수한 경우 처리"""
        return dish, dish_category
    
    def _process_day_slot(self, dish_day_html: Any, date: datetime, day: str, 
                         time: str, dish_type: Optional[str]) -> List[CafeteriaDish]:
        """일별 메뉴 처리"""
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
                    
                processed_item, processed_category = self._process_special_cases(
                    menu_item, current_category, time)
                    
                if processed_item:
                    dishes.append(CafeteriaDish(
                        cafeteria_id=self.cafeteria.id,
                        date=date.isoformat(),
                        day=day,
                        dish_type=dish_type,
                        dish_category=processed_category,
                        time=time,
                        dish_name=processed_item
                    ))
                    
        return dishes

    def _process_time_slot(self, time_index: int, date_list: List[datetime], 
                          dish_time_htmls: List[Any]) -> List[CafeteriaDish]:
        """시간대별 메뉴 처리"""
        dishes = []
        dish_type = self.DISH_TYPE_LIST[time_index] if self.cafeteria.form_type == 2 else None
        time = self._get_time_for_cafeteria(time_index)
        
        dish_time_html = dish_time_htmls[time_index]
        dish_day_htmls = dish_time_html.find_all('td')
        
        for day_index, day in enumerate(self.DAY_LIST):
            if day_index >= len(dish_day_htmls):
                continue
                
            date = date_list[day_index]
                
            new_dishes = self._process_day_slot(dish_day_htmls[day_index], date, day, time, dish_type)
            dishes.extend(new_dishes)
            
        return dishes
    
    def get_scraper_name(self):
        return f"식단 메뉴"

    def delete_past_data(self):
        """과거 데이터 삭제"""
        delete_past_dishes(self.cafeteria.id, get_midnight(datetime.now()))

    def scrape_data(self):
        """새로운 식당 데이터를 스크래핑하는 함수"""
        try:
            with self as scraper:
                scraper.driver.get(self.base_url)
                scraper.driver.implicitly_wait(10)
                
                parsed_html = BeautifulSoup(scraper.driver.page_source, 'html.parser')
                start_date, end_date, dishes = self._parse_menu_data(parsed_html)
                
                if dishes:
                    delete_dishes_by_date_range(self.cafeteria.id, start_date, end_date)
                    save_dishes(dishes, self.cafeteria.id)
                    print(f'[교내 식당] {self.cafeteria.campus_id}번 캠퍼스 {self.cafeteria.cafeteria_name_ko}의 '
                          f'새로운 식단 데이터 {len(dishes)}개를 스크래핑했습니다.')
        
        except Exception as e:
            context_message = f"{self.cafeteria.campus_id}번 캠퍼스 {self.cafeteria.cafeteria_name_ko} 식단 데이터 조회 실패"
            self.notify_failure(e, context_message)