from bs4 import BeautifulSoup

import api
# import pinecone
import libs.libs as libs
from libs.libs import get_links
from libs.libs import clean_page
from libs.libs import get_page
from libs.libs import remove_duplicates
from datetime import datetime
import libs.lib_embeddings as lib_embeddings


url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"
technology_list = ["AI", "Technology", "Privacy", "Cybersecurity"]

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
            metadata = {"category": technology_list[i], "url": url, "pagename": entry['title'], "date": date}

            page = get_page(url)
            if page.status_code == 403 :
                forbidden_links.append(url)
                continue

            clean_text = clean_page(url, page)

            ####################################
            
            num_tokens = lib_embeddings.num_tokens_from_string(clean_text, model)
            if  num_tokens > 16300: #limit is 16,385 
                chunks = libs.split_document(clean_text)
                print(len(chunks))


            # Creating input to clean text from HTML/XML code for pure text
            messages_1 = [{"role": "system", "content": api.system_content},
                        {"role": "user", "content": f"{clean_text}"}]
            response1 = libs.gpt_response(model, messages_1)
            cleaned_article = response1.choices[0].message.content



            # Uses LLM to summarizes article
            messages_2 = [{"role": "system", "content": api.system_content2},
                        {"role": "user", "content": cleaned_article}]
            response2 = libs.gpt_response(model, messages_2)
            summary = response2.choices[0].message.content

            #Update Meta data

            metadata["summary"] = summary

            lib_embeddings.write_to_file(metadata)
            acceptable_links_count += 1
            ##########################################
            # TODO
            # 1. Store into vector DB after scraping is completed.
            # 2. When re-scraping, search urls and make sure I'm not scraping duplicates done
            # 3. 
            
            # Save  in the vector database
    
    print("forbidden_links count", len(forbidden_links))
    print("acceptable_links_count", acceptable_links_count)