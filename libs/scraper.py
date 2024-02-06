from bs4 import BeautifulSoup

import api
import re
import openai
import libs.site_handler as site_handler
import libs.hyperdb as embeddings
import requests
from datetime import datetime
import string
import feedparser
from libs.sql_manager import SQLManager
import re

# NO VECTORS IN THIS CLASS
class Scraper:
    def __init__(self, urls,
                 gpt_model="gpt-3.5-turbo-16k") -> None:

        # I need a better way to find duplicates
        # each feed item will have some of the following or all:
        # Title, Summary, Authors, published date, Check tags

        self.gpt_model = gpt_model
        self.feed = []
        for url in urls:
            feed = feedparser.parse(url)
            if feed.bozo:
                continue;

            for entry in feed.entries:
                self.feed.append(entry)

        self.remove_duplicates(self.feed) #Remove duplicates earlier TODO

        # self.urls = remove_duplicates(self.urls)
        date = datetime.today().strftime('%Y-%m-%d')
            
        self.forbidden = []


        CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        num_titles = len(self.feed)
        self.metadata = {}  # TODO (urls, titles, entries, dates) just like a pandas df
        self.metadata["url"] = [self.feed[i].link for i in range(num_titles)]

        self.metadata["title"] = [self.feed[i].title for i in range(num_titles)]
        self.metadata["summary"] = [re.sub(CLEANR, '', self.feed[i].summary) if self.feed[i].summary is not None else None for i in range(num_titles)]
        self.metadata["date"] = [date for i in range(num_titles)]
        self.metadata["author"] = [[author.name for author in self.feed[i].authors]  if self.feed[i].authors is not None else None for i in range(num_titles)]

        self.categories = []                   
    
    def remove_duplicates(self, urls): 
        
        sql_manager = SQLManager()
        query = ("SELECT url, count(url) AS count FROM metadata GROUP by url;")
        existing_links = [link[0] for link in sql_manager.query(query)]

        query = ("SELECT title, count(title) AS count FROM metadata GROUP by title;")
        existing_titles = [title[0] for title in sql_manager.query(query)]
        
        
        my_set = []
        for i, article in enumerate(self.feed):
            isDup = False
            for key, value in article.items():
                if key == "link" or key == "title":
                    if value in existing_links or value in existing_titles:
                        isDup = True
                        continue
            if not isDup:
                my_set.append(article)
                    

        print("Not duplicated", len(my_set))
        print("Duplicated", len(self.feed))
        self.feed = my_set
    

    def entries(self):
        return self.feed

    def get_metadata(self) -> dict:
        return self.metadata

    def get_forbidden_links(self):
        return self.forbidden

    def remove_entry(self, index):
        for key in self.metadata:
            print(index)
            self.metadata[key].remove(index)
        pass

    #Makes API call to summarize the articles
    def summarize(self, url):
        clean_text = self.scrape_summary(url) 

        if clean_text is None:
            return clean_text

        if len(clean_text) > 98300:
            num_tokens = embeddings.num_tokens_from_string(clean_text, self.gpt_model)
            if  num_tokens > 16300: #limit is 16,385
                index = self.metadata["url"].index(url) 
                self.remove_entry(index)
                return None
                #pop from the list
            
        messages_1 = [{"role": "system", "content": api.system_content},
            {"role": "user", "content": f"{clean_text}"}]
        response1 = self.gpt_response(self.gpt_model, messages_1)
        cleaned_article = response1.choices[0].message.content

        return cleaned_article

    # MAkes api calls using either the title or the article summary, or both 
    # Separate to another class   
    def categorize(self):
        
        for i, summary in enumerate(self.metadata["summary"]):
            if summary is None:
                summary = self.metadata["summary"][i] = self.summarize(self.metadata.url[i])
                print("Summary; ", summary , "\n")

            num_tokens = embeddings.num_tokens_from_string(summary, self.gpt_model)
            if  num_tokens > 16300: #limit is 16,385 
                summary = self.metadata["title"][i] #Uses the title to categorize instead of the summary
 
            messages_2 = [{"role": "system", "content": api.system_content2},
                {"role": "user", "content": summary}]
            
            response2 = self.gpt_response(self.gpt_model, messages_2)
            category = response2.choices[0].message.content

            # Make it one word only 
            if ' ' in category:
                category = category.split(' ')[0]
            if '.' in category:
                category = category.split('.')[0]

            
            self.categories.append(category) # clean the punctuation
            
        self.metadata["category"] = self.categories

    # Scrapes articles
    # RSS links if there's no premilinary summary in the description. Occurs with Bozo links
    @staticmethod
    def scrape_summary(self, url) -> str:
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
    

    @staticmethod
    def split_document(document, chunk_size=2000):
        chunks = []
        for i in range(0, len(document), chunk_size):
            chunks.append(document[i:i+chunk_size])
        return chunks
    
    @staticmethod
    def gpt_response(model, message):
        return openai.ChatCompletion.create(
                    model=model,
                    messages=message
                )

    
        """
        documents = []
        with open("summaries.txt", "r") as f:
            for line in f:
                documents.append(json.loads(line))

        in_file  = [x['url'] for x in documents]
        
        dict = {}

        for key, value in urls.items():
            new_rss_links = []
            for article in value:
                new_rss_links.append( {
                    "url" :article['url'],
                    "title" :  article["title"]
                })
            
            dict[str(key)] = new_rss_links

        
        for key, value in dict.items():
            for article in dict[key]:
                if article['url'] in in_file:
                    dict[key].remove(article)    
            pass"""
    
    @staticmethod
    def REST_codes(status_code):
        if status_code == 200 :
            return True
        elif status_code == 403 or status_code == 202:
            return False