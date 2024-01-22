from bs4 import BeautifulSoup
import json
from selenium import webdriver
import re
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import requests
import openai
import headers

import tiktoken


def get_links(urls):
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as driver:
        sources = []

        for url in urls:
            driver.get(url)
            sources.append(driver.page_source)

    rss = []
    for page in sources:
        rss.append(json.loads(BeautifulSoup(page, 'lxml').get_text()))

    merged_dict = {}
    if len(rss) > 1:
        for i in rss:
            merged_dict = {**merged_dict, **i}

    return merged_dict

def get_page(url):
    page = requests.get(url)
    print(url, page.status_code)
    return page
    
def REST_codes(status_code):
    if status_code == 200 or status_code == 202:
        return True
    elif status_code == 403:
        return False

def get_with_header(url):
    from seleniumwire import webdriver
    driver = webdriver.Chrome()
    
    driver.request_interceptor = headers.header_marketpost
    driver.get(url)

    for request in driver.requests:
        if request.response:
            print(
                request.url,
                request.response.status_code,
                request.response.headers['Content-Type']
            )

    del driver.requests
    return True


def clean_page(url, page):

    if ("arxiv" in url):
        return clean_arxiv(page)
    
    tag = re.compile(r'<[^>]+>')
    soup = BeautifulSoup(page.text, 'html.parser').find_all('p')

    paragraphs = []
    for x in soup:
        paragraphs.append(str(x))

    paragraphs = ' '.join(paragraphs)
    clean_text = re.sub(tag, '', paragraphs)

    return clean_text

def clean_arxiv(page):

    clean_text = BeautifulSoup(page.text, 'html.parser').find(property="og:description")['content']
    return clean_text

def remove_duplicates(urls):
    from collections import ChainMap
    documents = []

    with open("summaries.txt", "r") as f:
        for line in f:
            documents.append(json.loads(line))

    in_file  = [x['url'] for x in documents]
    
    dict = {}

    for key, value in urls.items():
        new_rss_links = []
        for article in value:
            new_rss_links.append( {
                "url" :article['url'],
                "title" :  article["title"]
            })
        
        dict[str(key)] = new_rss_links

    
    for key, value in dict.items():
        for article in dict[key]:
            if article['url'] in in_file:
                dict[key].remove(article)
    
    return dict
    

def split_document(document, chunk_size=2000):
    chunks = []
    for i in range(0, len(document), chunk_size):
        chunks.append(document[i:i+chunk_size])
    return chunks

def split_sentences(document):
    return document.split(". ")


def gpt_response(model, message):
    return openai.ChatCompletion.create(
                model=model,
                messages=message
            )

def gpt_embeddings(batch, model):
    response = openai.Embedding.create(input=batch, model=model)
    return response

def upsert_documents(embeddings, summary, metadata, index):

    # Creating embeddings for each document and preparing for upsert
    upsert_items = []
    
    embedding = [record['embedding'] for record in embeddings]
    # Include the original document text in the metadata
    document_metadata = metadata.copy()
    document_metadata['original_text'] = summary
    upsert_items.append((f"{metadata['pagename']}", embedding[0], document_metadata))

    # Upsert to Pinecone
    index.upsert(upsert_items)

