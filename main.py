from libs.scraper import Scraper

from datetime import datetime

import libs.urls as urls
import numpy as np
from libs.hyperdb import HyperDB
from libs.sql_manager import SQLManager
from libs.hyperdb import create_embedding
import pickle
from libs.hyperdb import load_model_embeddings

def scrape_rss():
    date = datetime.today().strftime('%Y-%m-%d')

    article_scraper = Scraper(urls.rss_urls)
    article_scraper.categorize()
    documents = article_scraper.get_metadata() #dictionary class

    mysql = SQLManager()
    
    tokenizer, model = load_model_embeddings()

    for i, title in enumerate(documents["title"]):
 
        category = "Temp" # documents["category"][i]
        url = documents["url"][i]
        author = ', '.join(documents["author"][i]) 
        date = documents["date"][i]
        summary = documents["summary"][i]

        print(category, url, title, author, date)
        summary_vector = pickle.dumps(create_embedding(tokenizer, model, summary)[0].numpy())
        category_vector = pickle.dumps(create_embedding(tokenizer, model, category)[0].numpy())

        mysql.insert_summary(summary)
        mysql.insert_metadata(category, url, title, author, date)
        mysql.insert_embedding(summary_vector, category_vector)
        mysql.insert_category(category, category_vector)
        mysql.commit()
        exit()

def query_rss(queried_text):
    sql_manager = SQLManager()
    
    # For removing duplicate links TODO
    embeddings = sql_manager.sql_to_pandas("embeddings")
    summary = sql_manager.sql_to_pandas("summary")
    metadata = sql_manager.sql_to_pandas("metadata")
    category = sql_manager.sql_to_pandas("categories")

    embeddings["summary_vector"] = embeddings.apply(lambda row: pickle.loads(row["summary_vector"]), axis=1)
    embeddings["category_vector"] = embeddings.apply(lambda row: pickle.loads(row["category_vector"]), axis=1)
    
    metadata_list = [metadata.loc[i, :].values.flatten().tolist() for i in range(embeddings.shape[0])]

    
    tmp = embeddings["summary_vector"].tolist() 
    vectors_summaries = None
    for vector in tmp:
        if vectors_summaries is None:
                    vectors_summaries = np.empty((0, len(vector)), dtype=np.float32)
        vectors_summaries = np.vstack([vectors_summaries, vector]).astype(np.float32)

    tmp = embeddings["category_vector"].tolist()
    vectors_categories = None
    for vector in tmp:
        if vectors_categories is None:
                    vectors_categories = np.empty((0, len(vector)), dtype=np.float32)
        vectors_categories = np.vstack([vectors_categories, vector]).astype(np.float32)

    db_summaries = HyperDB(documents = summary["summary"].tolist(), vectors = vectors_summaries, metadata=metadata_list )
    db_categories = HyperDB(documents = summary["summary"].tolist(), vectors = vectors_categories, metadata=metadata_list )
    
    results_sum = db_summaries.query(queried_text, top_k=8)
    results_cat = db_categories.query(queried_text, top_k=8)

    for result in results_sum:
           print(result[0][0])

    print('\n\n')
    for result in results_cat:
        print(result[0])

if __name__ == '__main__':
    # THis queries DB 
    command = input("scrape or query? \n")

    if command == "scrape":
          scrape_rss()
    else:
          query_rss(command)