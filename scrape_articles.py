from bs4 import BeautifulSoup

import api
import pinecone
import libs
from libs import get_links
from libs import filter_page
from libs import clean_page
from libs import get_page
from datetime import datetime

import embeddings

url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"
technology_list = ["AI", "Technology", "Privacy", "Cybersecurity"]

model = "gpt-3.5-turbo-16k"
index_name = "rss"
date = datetime.today().strftime('%Y-%m-%d')

pinecone.init(api_key=api.pinecone_key, environment="gcp-starter")
index = pinecone.Index(index_name=index_name)

tokenizer, embedings_model = embeddings.load_model_embeddings()


if __name__ == "__main__":
    rss_all = get_links([url, url2])

    forbidden_links = []
    filtered_links = []

    for i, theme in enumerate(rss_all):
        for entry in rss_all[theme]:

            url = entry['url']
            metadata = {"category": technology_list[i], "url": url, "pagename": entry['title'], "date": date}

            if filter_page(url):
                filtered_links.append(url) 

            page = get_page(url)
            if page.status_code == 403 :
                forbidden_links.append(url)
                continue

            clean_text = clean_page(page)

            
            num_tokens = libs.num_tokens_from_string(clean_text, model)
            if  num_tokens > 16300: #limit is 16,385 
                chunks = libs.split_document(clean_text)
                # libs.upsert_documents(chunks, clean_text, metadata, index)
                print(len(chunks))

            messages_1 = [{"role": "system", "content": api.system_content},
                        {"role": "user", "content": f"{clean_text}"}]
            response1 = libs.gpt_response(model, messages_1)
            cleaned_article = response1.choices[0].message.content

            messages_2 = [{"role": "system", "content": api.system_content2},
                        {"role": "user", "content": cleaned_article}]
            response2 = libs.gpt_response(model, messages_2)
            summary = response2.choices[0].message.content

            # Creating embeddings
            sentences = summary.split(". ")
            embeddings = embeddings.create_embedding(tokenizer, embedings_model, sentences)

            tmp = [url, str(response2.choices[0].message.content), date, '\n']
            with open(f'messages - {date}.txt', 'a') as f:
                f.write(str(','.join(tmp)))

            embeddings_dict  = {**metadata, "embeddings": embeddings.tolist()}

            with open(f'embeddings - {date}.txt', 'a') as f:
                f.write( str(embeddings_dict) )

            exit()
   
    #  Find a way to remove too large articles or reduce tokens, or find a number of tokens