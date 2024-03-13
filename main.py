# test.py
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import os
import sys

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

url = 'https://www.gnu.ac.kr/cse/na/ntt/selectNttList.do?mi=17093&bbsId=4753'

driver.get(url)
driver.implicitly_wait(5)
sleep(3) 

html = driver.page_source

print(html)