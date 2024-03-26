import time
from src.notice.scraper import Notice_Scraper
from src.cafeteria.scraper import Cafeteria_Scraper
from multiprocessing import Process
from src.supabase_utils import supabase

def get_colleges():
    colleges = supabase().table('college').select('college_en, etc_value').execute().data
    college_en_list = [college['college_en'] for college in colleges if college['etc_value'] == False]
    college_en_list.append('etc')
    return college_en_list

def run_notice_scraper(college):
    notice_scraper = Notice_Scraper(college)
    notice_scraper.scrape_notice_data()

if __name__ == '__main__':
    start_time = time.time()
    colleges = get_colleges()

    processes = []
    for college in colleges:
        process = Process(target=run_notice_scraper, args=(college,))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

    # cafeteria_scraper = Cafeteria_Scraper()
    # cafeteria_scraper.scrape_cafeteria_dish_data()
    
    print(f"모든 단과대학의 스크래핑이 완료되었습니다. 소요시간: {time.time() - start_time}초")