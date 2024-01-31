from bs4 import BeautifulSoup

import api
# import pinecone
import libs.site_handler as site_handler
from libs.site_handler import get_links
from libs.site_handler import clean_page
from libs.site_handler import get_page
from libs.site_handler import remove_duplicates
from datetime import datetime
import libs.embeddings as embeddings

import libs.sql_manager as sql_manager
# https://www.zenrows.com/blog/beautifulsoup-403#moderate-the-frequency-of-requests

url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"

model = "gpt-3.5-turbo-16k"
index_name = "rss"
date = datetime.today().strftime('%Y-%m-%d')


if __name__ == "__main__":
    rss_all = get_links([url, url2])


    rss_links = remove_duplicates(rss_all)
    del(rss_all)

    forbidden_links = []
    acceptable_links_count = 0
    filtered_links = []

    for i, theme in enumerate(rss_links):
        for entry in rss_links[theme]:

            url = entry['url']
            metadata = { "url": url, "pagename": entry['title'], "date": date}

            page = get_page(url)
            if page.status_code == 403:
                forbidden_links.append(url)
                continue
            elif page.status_code == 202:
                continue

            clean_text, metadata['pagename'] = clean_page(url, page, metadata['pagename'])

            ####################################
            
            num_tokens = embeddings.num_tokens_from_string(clean_text, model)
            if  num_tokens > 16300: #limit is 16,385 
                chunks = site_handler.split_document(clean_text)
                print(num_tokens)
                continue


            # Creating input to clean text from HTML/XML code for pure text
            messages_1 = [{"role": "system", "content": api.system_content},
                        {"role": "user", "content": f"{clean_text}"}]
            response1 = site_handler.gpt_response(model, messages_1)
            cleaned_article = response1.choices[0].message.content
            
            print(cleaned_article, "\n")

            print(entry['title'])
            # Uses LLM to find a category for the article
            messages_2 = [{"role": "system", "content": api.system_content2},
                        {"role": "user", "content": cleaned_article}]
            response2 = site_handler.gpt_response(model, messages_2)
            category = response2.choices[0].message.content

            print(category)

            metadata['category'] = category
            #Update Meta data
            # continue
            metadata["summary"] = cleaned_article

            sql_manager.write_to_sql(metadata)
            embeddings.write_to_file(metadata)
            acceptable_links_count += 1


    print("forbidden_links count", len(forbidden_links))
    print("acceptable_links_count", acceptable_links_count)