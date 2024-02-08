from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import libs.headers as headers


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

def get_with_header(url):
    driver = webdriver.Chrome()
    
    driver.request_interceptor = headers.header_marketpost
    driver.get(url)

    for request in driver.requests:
        if request.response:
            print(
                request.url,
                request.response.status_code,
                request.response.headers['Content-Type']
            )

    del driver.requests
    return True






