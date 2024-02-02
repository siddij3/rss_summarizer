from scrape_articles import Scraper

from datetime import datetime

import libs.urls as urls

from libs.sql_manager import SQLManager
from libs.embeddings import create_embedding
import pickle

date = datetime.today().strftime('%Y-%m-%d')

from libs.embeddings import load_model_embeddings


    
if __name__ == '__main__':


# # Keep the scraping and the SQL stuff decoupled.
    article_scraper = Scraper(urls.rss_urls)
    
    # article_scraper.categorize()
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


        mysql.insert_summary( summary)
        mysql.insert_metadata(category, url, title, author, date)
        mysql.insert_embedding( summary_vector, category_vector)
        mysql.insert_category(category, category_vector)
        mysql.commit()
        exit()

    # I should create the embeddings out here?
    # sql_manager.write_to_sql(metadata)
    # """
    # 4. 
    # """
    # embeddings.write_to_file(metadata)

    # print("forbidden_links count", len(forbidden_links))
    # print("acceptable_links_count", acceptable_links_count