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

from libs import get_links

url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"
technology_list = ["AI", "Technology", "Privacy", "Cybersecurity"]




if __name__ == "__main__":
    rss_all= get_links([url, url2])
    
    tag = re.compile(r'<[^>]+>')

    messages = []
    forbidden_links = []

    for i, theme in enumerate(rss_all):
        for entry in rss_all[theme]:
            print(entry['url'])
            continue

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

    #  Find a way to remove too large articles or reduce tokens, or find a number of tokens