from bs4 import BeautifulSoup

import api
import pinecone
import libs
from libs import get_links
from libs import filter_page
from libs import clean_page
from libs import get_page

url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"
technology_list = ["AI", "Technology", "Privacy", "Cybersecurity"]

model = "gpt-4"
index_name = "rss"

pinecone.init(api_key=api.pinecone_key, environment="gcp-starter")

index = pinecone.Index(index_name=index_name)



if __name__ == "__main__":
    rss_all= get_links([url, url2])

    forbidden_links = []
    filtered_links = []

    for i, theme in enumerate(rss_all):
        for entry in rss_all[theme]:

            url = entry['url']
            metadata = {"pagename": entry['title']}

            if filter_page(url):
                filtered_links.append(url) 

            page = get_page(url)
            if page.status_code == 403 :
                forbidden_links.append(url)
                continue

            clean_text = clean_page(page)

            
            num_tokens = libs.num_tokens_from_string(clean_text, model)
            if  num_tokens > 8000: #limit is 8192
                chunks = libs.split_document(clean_text)
                libs.upsert_documents(chunks, clean_text, metadata, index)
                print(len(chunks))
            print(num_tokens)
            
            

            technology = technology_list[i]

            messages_1 = [{"role": "system", "content": api.system_content},
                        {"role": "user", "content": f"{clean_text}"}]

            response1 = libs.gpt_response(model, messages_1)
            
            clean_article = response1.choices[0].message.content

            messages_2 = [{"role": "system", "content": api.system_content2},
                        {"role": "user", "content": clean_article}]
            response2 = libs.gpt_response(model, messages_2)
            
            print(response2.choices[0].message.content)

            with open('messages.txt', 'a') as f:
                f.write(str(entry['url']))
                f.write(": ")
                f.write(str(response2.choices[0].message.content))
                f.write(",\n")

    #  Find a way to remove too large articles or reduce tokens, or find a number of tokens