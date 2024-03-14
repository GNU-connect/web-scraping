from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium_utils import get_driver

driver = get_driver()

url = 'https://www.gnu.ac.kr/cse/na/ntt/selectNttList.do?mi=17093&bbsId=4753'

driver.get(url)
driver.implicitly_wait(5)
sleep(3) 

html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

print(soup)
