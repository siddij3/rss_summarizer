from scrape_articles import Scraper
from scrape_articles import scrape
from datetime import datetime
import feedparser
import libs.urls as urls
from hyperdb import HyperDB


date = datetime.today().strftime('%Y-%m-%d')


    
if __name__ == '__main__':


# # Keep the scraping and the SQL stuff decoupled.
    article_scraper = Scraper(urls.rss_urls)
    # article_scraper.categorize()
    print(article_scraper.get_metadata()["author"])

    

    # I should create the embeddings out here?
    # sql_manager.write_to_sql(metadata)
    """
    1. Connect to mydb
    2. Get cursor
    3. Split values appropriately for each table
    4. 
    """
    # embeddings.write_to_file(metadata)

    # print("forbidden_links count", len(forbidden_links))
    # print("acceptable_links_count", acceptable_links_count)