import time
from src.notice.scraper import Scraper
from multiprocessing import Process
from src.supabase_utils import supabase

def get_colleges():
    colleges = supabase().table('college').select('college_en').execute().data
    college_en_list = [college['college_en'] for college in colleges]
    return college_en_list

def run_notice_scraper(college):
    scraper = Scraper(college)
    scraper.scrape_notice_data()

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
    
    print(f"모든 단과대학의 스크래핑이 완료되었습니다. 소요시간: {time.time() - start_time}초")