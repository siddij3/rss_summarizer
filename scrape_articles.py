from bs4 import BeautifulSoup
import json
from html.parser import HTMLParser
from selenium import webdriver
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import requests
import openai
import urllib
import api

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
tag = re.compile(r'<[^>]+>')

messages = []
forbidden_links = []

technology_list = ["AI", "Technology", "Privacy", "Cybersecurity"]


for i, theme in enumerate(rss_1):
    for entry in rss_1[theme]:

        

        if ("arxiv" in entry['url']):
            # Make a function for PDFs here
            continue
        page = requests.get(entry['url'])

        print(entry['url'], page.status_code)
        if page.status_code == 403 :
            forbidden_links.append(entry['url'])
            continue

        soup = BeautifulSoup(page.text, 'html.parser').find_all('p')

        paragraphs = []
        for x in soup:
            paragraphs.append(str(x))

        paragraphs = ' '.join(paragraphs)
        clean_text = re.sub(tag, '', paragraphs)

        technology = technology_list[i]
        response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": api.system_content},
                {"role": "user", "content": clean_text}]
                )
        
        clean_article = response.choices[0].message.content

        response2 = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": api.system_content2},
                    {"role": "user", "content": clean_article}]
        )
        print(response2.choices[0].message.content)
        messages.append([entry['url'], response2.choices[0].message.content])
    

with open('messages.txt', 'w') as f:
    f.write(str(messages))