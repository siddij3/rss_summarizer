from bs4 import BeautifulSoup
import json
from html.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import requests
import urllib

url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"

with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as driver:
    driver.get(url)
    first = driver.page_source

    # driver.get(url2)
    # second = driver.page_source

rss_1 = json.loads(BeautifulSoup(first).get_text())
# rss_2 = json.loads(BeautifulSoup(second).get_text())

# merged_dict = {**rss_1, **rss_2}

for theme in rss_1:
    for entry in rss_1[theme]:
       page = requests.get(entry['url']).text
       soup = BeautifulSoup(page, 'html.parser').find_all('p')
       print(soup)