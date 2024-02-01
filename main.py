from scrape_articles import Scraper
from scrape_articles import scrape
from datetime import datetime


url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"

model = "gpt-3.5-turbo-16k"
index_name = "rss"
date = datetime.today().strftime('%Y-%m-%d')

if __name__ == '__main__':


# Keep the scraping and the SQL stuff decoupled.
    article_scraper = Scraper([url, url2])

   
    rss_links = article_scraper.links()
    for i, theme in enumerate(rss_links):
        for entry in rss_links[theme]:
            print(entry)

        # combine metadata here
