

import api
from libs.scraper import Scraper
from datetime import datetime
import libs.urls as urls
import numpy as np
from libs.NLP import HyperDB
from libs.db_rss_feeds import RSSDatabase


import pickle
from fastapi import FastAPI
import openai   

from libs.NLP import Tokens
from libs.NLP import ChatBotHandler
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')

app = FastAPI()


def scrape_rss():
    
    article_scraper = Scraper(urls.rss_urls)
    article_scraper.categorize()
    documents = article_scraper.get_metadata() #dictionary class
    
    myrssdb = RSSDatabase()
    mytokens = Tokens()
    
    for i, title in enumerate(documents["title"]):
 
        category = documents["category"][i]
        url = documents["url"][i]
        author = ', '.join(documents["author"][i]) 
        date = documents["date"][i]
        summary = documents["summary"][i]

        # I could abstract this another layer too. Maybe later TODO
        summary_vector = pickle.dumps(mytokens.create_embedding(summary))
        category_vector = pickle.dumps(mytokens.create_embedding(category))

        myrssdb.insert_article_entry(summary, summary_vector, 
                                   category, category_vector, 
                                   url,      title, 
                                   author,   date)

        myrssdb.commit()

    myrssdb.end_connection()
    

def query_rss():
    myrssdb = RSSDatabase()

    categories_count = myrssdb.query_categories()

    embeddings = myrssdb.query_table_all_rows('embeddings')
    summary = myrssdb.query_table_all_rows('summary')
    metadata = myrssdb.query_table_all_rows('metadata')
    category = myrssdb.query_table_all_rows('categories')


    # Abstract away from knowing the table schemas....
    # summary_vector_list = [pickle.loads(row[2]) for row in embeddings]
    category_vector_list = [pickle.loads(row[2]) for row in embeddings]
    summary_list = [row[1] for row in summary]
    
    

    def get_vector(embeddings_list):
        vectors = None
        for vector in embeddings_list:
            if vectors is None:
                        vectors = np.empty((0, len(vector)), dtype=np.float32)
            vectors = np.vstack([vectors, vector]).astype(np.float32)
        return vectors
    
    # vectors_summaries = get_vector(summary_vector_list)
    vectors_categories = get_vector(category_vector_list)
   
    db_categories = HyperDB(documents=summary_list, vectors = vectors_categories, metadata=metadata )

    gpt_bot = ChatBotHandler("gpt-4-turbo-preview")
    query = {}
    for category, count in categories_count:
        results_cat = db_categories.query(category, top_k=count)
        # summary: str(article[0][0])
        #     url: article[0][1][1]
        #   title: article[0][1][2].strftime('%Y-%m-%d')
    
        summaries = [str(article[0][0]) for article in results_cat]
        sources = [(str(article[0][1][2]) , str(article[0][1][1])) for article in results_cat]

        stitch = (f"You will be given a list of topics under {category}. "
                           "Write a few paragraphs that stitches these topics together.")

        context_summary = gpt_bot.message_maker(stitch, str(summaries))[0].message.content

        query[category] = {
             "Context Summary": context_summary,
             "Sources": sources
        }
        
        return query

    



@app.get("/query")
def query_articles():
    all = query_rss()
    return all


@app.get("/")
async def scrape_articles():
    scrape_rss()
    return {"Documents": "Scraping"}


    
if __name__ == "__main__":
    query_rss()