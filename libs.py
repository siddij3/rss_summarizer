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

def get_links(urls):

    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as driver:
        sources = []

        for url in urls:
            driver.get(url)
            sources.append(driver.page_source)

    rss = []
    for page in sources:
        rss.append(json.loads(BeautifulSoup(page, 'lxml').get_text()))

    merged_dict = {}
    if len(rss) > 1:
        for i in rss:
            merged_dict = {**merged_dict, **i}

    return merged_dict




if __name__ == "__main__":

    print("heo")