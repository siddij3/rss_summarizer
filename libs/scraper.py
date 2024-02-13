from bs4 import BeautifulSoup
import re
import requests

from datetime import datetime


import feedparser
from libs.db_rss_feeds import RSSDatabase
import re

import libs.message_prompts as message_prompts
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import libs.headers as headers
from libs.NLP import ChatBotHandler
from libs.NLP import Tokens
import asyncio


class SiteHandler:
    def __init__(self, 
                 urls = None):
        pass

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
    
    def REST_codes(self, status_code):
        if status_code == 200 :
            return True
        elif status_code == 403 or status_code == 202:
            return False


# NO VECTORS IN THIS CLASS
class Scraper():
    def __init__(self, 
                 urls=None):
    
        # I need a better way to find duplicates
        # each feed item will have some of the following or all:
        # Title, Summary, Authors, published date, Check tags  

        self.urls = urls  
        self.metadata = {}  
        self.CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.todo = asyncio.Queue()

    async def run(self):

        self.feed = []
        feed = [
                asyncio.create_task(feedparser.parse(url)) for url in self.urls
                ]
        await self.todo.join()

        print(len(feed))
        exit()

        for url in self.urls:
            feed = feedparser.parse(url)
            if feed.bozo:
                #Try the web-scraper route
                continue;

            for entry in feed.entries:
                self.feed.append(entry)

        self.remove_duplicates() #Remove duplicates earlier TODO



        num_titles = len(self.feed)
        self.metadata["url"] = [self.feed[i].link for i in range(num_titles)]
        self.metadata["title"] = [self.feed[i].title for i in range(num_titles)]
        self.metadata["summary"] = [re.sub(self.CLEANR, '', self.feed[i].summary) if self.feed[i].summary is not None else None for i in range(num_titles)]
        self.metadata["date"] = [self.date for i in range(num_titles)]
        self.metadata["author"] = [[author.name for author in self.feed[i].authors]  if self.feed[i].authors is not None else None for i in range(num_titles)]

            
        self.categories = []         

        self.ChatBotHandler = ChatBotHandler()
        self.Tokens = Tokens()

    # Decouple later?
    async def remove_duplicates(self): 
        
        myrssdb = RSSDatabase()
        existing_links =  myrssdb.query_article_links()
        existing_titles =  myrssdb.query_article_titles()
        
        my_set = []
        for _, article in enumerate(self.feed):
            isDup = False
            for key, value in article.items():
                if key == "link" or key == "title":
                    if value in existing_links or value in existing_titles:
                        isDup = True
                        continue
            if not isDup:
                my_set.append(article)
                    

        print("Unique Articles", len(my_set))
        print("Total articles", len(self.feed))
        self.feed = my_set
    

    async def get_metadata(self) -> dict:
        return self.metadata

    async def remove_entry(self, index):
        for key in self.metadata:
            print(index)
            self.metadata[key].remove(index)
        pass

    #Makes API call to summarize the articles
    async def summarize(self, url):
        clean_text = self.scrape_summary(url) 

        if clean_text is None:
            return clean_text


        if not self.check_size(clean_text): 
            self.remove_entry(self.metadata["url"].index(url))
            return None
 
            
        cleaned_article = self.ChatBotHandler.message_maker(message_prompts.summary, clean_text)[0].message.content # f"{clean_text}" why did i have this?
        return cleaned_article
    
    async def check_size(self, text):
        if len(text) > 98300:
            
            num_tokens = self.Tokens.num_tokens_from_string(text)
            if  num_tokens > 16300:  #limit is 16,385
                return False
            return False
        return True

    # Do asynch?
    async def categorize(self):
        for i, summary in enumerate(self.metadata["summary"]):
            if summary is None:
                summary = self.metadata["summary"][i] = self.summarize(self.metadata.url[i])
                print("Summary; ", summary , "\n")

            if not self.check_size(summary): 
                summary = self.metadata["title"][i] #Uses the title to categorize instead of the summary
 
            category = self.ChatBotHandler.message_maker(message_prompts.category, summary)[0].message.content # f"{clean_text}" why did i have this?
            
            # Make it one word only 
            if ' ' in category:
                category = category.split(' ')[0]
            if '.' in category:
                category = category.split('.')[0]
            if ':' in category:
                category = category.split(':')[0]

            self.categories.append(category.lower()) # clean the punctuation

            
        self.metadata["category"] = self.categories

    # Scrapes articles
    # RSS links if there's no premilinary summary in the description. Occurs with Bozo links
        
    # import html.parser
    async def scrape_summary(self, url) -> str:
        # This is to get the summaries if there is none
        page = requests.get(url)
        
        if self.REST_codes(page.status_code) is False:
            self.forbidden.append(url)
            return None

        if ("arxiv" in url):
            clean_text = BeautifulSoup(page.text, 'html.parser').find(property="og:description")['content']
            title = title.split("(arX   ")[0]
            return clean_text, title
        
        tag = re.compile(r'<[^>]+>')
        soup = BeautifulSoup(page.text, 'html.parser').find_all('p')

        paragraphs = []
        for x in soup:
            paragraphs.append(str(x))

        paragraphs = ' '.join(paragraphs)
        clean_text = re.sub(tag, '', paragraphs)

        return clean_text
    
    
class SiteClassifier(Scraper):
    def __init__(self, urls, chatbot_model="gpt-3.5-turbo-16k") -> None:
        super().__init__(urls, chatbot_model)

        pass

 