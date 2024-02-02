from bs4 import BeautifulSoup

import api
import re
import openai
import libs.site_handler as site_handler
import libs.hyperdb as embeddings
import requests
from datetime import datetime

import feedparser


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

        # self.urls = remove_duplicates(self.urls)
        date = datetime.today().strftime('%Y-%m-%d')
                
        self.forbidden = []

        num_titles = len(self.feed)
        self.metadata = {}  # TODO (urls, titles, entries, dates) just like a pandas df
        self.metadata["url"] = [self.feed[i].link for i in range(num_titles)]

        self.metadata["title"] = [self.feed[i].title for i in range(num_titles)]
        self.metadata["summary"] = [self.feed[i].summary if self.feed[i].summary is not None else None for i in range(num_titles)]
        self.metadata["date"] = [date for i in range(num_titles)]
        self.metadata["author"] = [[author.name for author in self.feed[i].authors]  if self.feed[i].authors is not None else None for i in range(num_titles)]

        self.categories = []                   
            
    def entries(self):
        return self.feed

    def get_metadata(self) -> dict:
        return self.metadata

    def get_forbidden_links(self):
        return self.forbidden

    #Makes API call to summarize the articles
    def summarize(self, url):
        clean_text = self.scrape_summary(url) 
        if clean_text is None:
            return clean_text

        num_tokens = embeddings.num_tokens_from_string(clean_text, self.gpt_model)
        if  num_tokens > 16300: #limit is 16,385 
            return None
            #pop from the list
            
        messages_1 = [{"role": "system", "content": api.system_content},
            {"role": "user", "content": f"{clean_text}"}]
        response1 = site_handler.gpt_response(self.gpt_model, messages_1)
        cleaned_article = response1.choices[0].message.content

        return cleaned_article

    # MAkes api calls using either the title or the article summary, or both    
    def categorize(self):
        
        for i, summary in enumerate(self.metadata["summary"]):
            if summary is None:
                summary = self.metadata["summary"][i] = self.summarize(self.metadata.url[i])
                print(summary)

            messages_2 = [{"role": "system", "content": api.system_content2},
                {"role": "user", "content": summary}]
            response2 = site_handler.gpt_response(self.gpt_model, messages_2)
            category = response2.choices[0].message.content
            print(category)
            self.categories.append(category) # clean the punctuation
            
        self.metadata["category"] = self.categories

    # Scrapes articles
    # RSS links if there's no premilinary summary in the description. Occurs with Bozo links
    @staticmethod
    def scrape_summary(self, url) -> str:
        # This is to get the summaries if there is none
        page = requests.get(url)
        
        if site_handler.REST_codes(page.status_code) is False:
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

    def remove_duplicates(self, urls): # TODO   
        # Get links from SQL, then pop the ones that match
        # Or look over github again cuz idr
        pass
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
