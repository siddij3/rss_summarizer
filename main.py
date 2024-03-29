from libs.scraper import Scraper

from datetime import datetime

import libs.urls as urls
import numpy as np
from libs.hyperdb import HyperDB
from libs.sql_manager import SQLManager
from libs.hyperdb import create_embedding
import pickle
from libs.hyperdb import load_model_embeddings
from typing import Union
from fastapi import FastAPI
import openai   


app = FastAPI()


def get_vector(embeddings_list):

    vectors = None
    for vector in embeddings_list:
        if vectors is None:
                    vectors = np.empty((0, len(vector)), dtype=np.float32)
        vectors = np.vstack([vectors, vector]).astype(np.float32)
    return vectors


def scrape_rss():
    date = datetime.today().strftime('%Y-%m-%d')

    article_scraper = Scraper(urls.rss_urls)
    article_scraper.categorize()
    documents = article_scraper.get_metadata() #dictionary class

    mysql = SQLManager()
    
    tokenizer, model = load_model_embeddings()

    for i, title in enumerate(documents["title"]):
 
        category = documents["category"][i]
        url = documents["url"][i]
        author = ', '.join(documents["author"][i]) 
        date = documents["date"][i]
        summary = documents["summary"][i]

        summary_vector = pickle.dumps(create_embedding(tokenizer, model, summary)[0].numpy())
        category_vector = pickle.dumps(create_embedding(tokenizer, model, category)[0].numpy())

        mysql.insert_summary(summary)
        mysql.insert_metadata(category, url, title, author, date)
        mysql.insert_embedding(summary_vector, category_vector)
        mysql.insert_category(category, category_vector)
        mysql.commit()
    

def query_rss():
    sql_manager = SQLManager()
    query = ("SELECT category, count(category) AS count FROM metadata GROUP by category;")

    results = sql_manager.query(query)
    categories = [category for category, count in results]

    # For removing duplicate links TODO
    embeddings = sql_manager.sql_to_pandas("embeddings")
    summary = sql_manager.sql_to_pandas("summary")
    metadata = sql_manager.sql_to_pandas("metadata")
    category = sql_manager.sql_to_pandas("categories")

    embeddings["summary_vector"] = embeddings.apply(lambda row: pickle.loads(row["summary_vector"]), axis=1)
    embeddings["category_vector"] = embeddings.apply(lambda row: pickle.loads(row["category_vector"]), axis=1)
    
    metadata_list = [metadata.loc[i, :].values.flatten().tolist() for i in range(embeddings.shape[0])]
    

    vectors_summaries = get_vector(embeddings["summary_vector"].tolist() )
    vectors_categories = get_vector(embeddings["category_vector"].tolist() )
   
    db_summaries = HyperDB(documents = summary["summary"].tolist(), vectors = vectors_summaries, metadata=metadata_list )
    db_categories = HyperDB(documents = summary["summary"].tolist(), vectors = vectors_categories, metadata=metadata_list )
    


    query = {}
    for category in categories:
        results_cat = db_categories.query(category, top_k=15)
        # summary: str(article[0][0])
        # url: article[0][1][1]
        # date: article[0][1][-1].strftime('%Y-%m-%d')
    
        summaries = [str(article[0][0]) for article in results_cat]
        sources = [(str(article[0][1][2]) , str(article[0][1][1])) for article in results_cat]

        system_content3 = f"You will be given a list of topics under {category}. Write a few paragraphs that stitches these topics together."

        gtp_message = [{"role": "system", "content": system_content3},
                        {"role": "user", "content": str(summaries)}]
        response = openai.ChatCompletion.create(
                    model="gpt-4-turbo-preview",
                    messages=gtp_message
                )

        context_summary = response.choices[0].message.content

        query[category] = {
             "Context Summary": context_summary,
             "Sources": sources
        }
        
        return query
        # query[category] = [[str(article[0][0]), str(article[0][1][1]), str(article[0][1][-1].strftime('%Y-%m-%d'))]  for article in results_cat ]
        


    



@app.get("/query")
def query_articles():
    all = query_rss()
    return all


@app.post("/")
async def scrape_articles():
    scrape_rss()
    return {"Documents": "Scraping"}


    
if __name__ == "__main__":
    scrape_rss()