
import json
import api

import libs.site_handler as site_handler

from libs.embeddings import create_embedding
from libs.embeddings import load_model_embeddings

# from sklearn.feature_extraction.text import CountVectorizer
# from nltk.corpus import stopwords
# from sentence_transformers import SentenceTransformer
# from umap import UMAP
# from hdbscan import HDBSCAN
# from bertopic import BERTopic

TF_ENABLE_ONEDNN_OPTS=0


def get_category(model, article):
    messages = [{"role": "system", "content": api.system_content2},
                        {"role": "user", "content": article}]
    response2 = site_handler.gpt_response(model, messages)
    category = response2.choices[0].message.content

    return category.split('\n')

if __name__ == "__main__":
    import mysql.connector



    documents = []
    with open("summaries.txt", "r") as f:
        for line in f:
            documents.append(json.loads(line))

    

    mydb = mysql.connector.connect(
        host="localhost",
        user="junaid",
        password="junaid",
        database="rss_feeds",
        auth_plugin='mysql_native_password'
    )

    mycursor = mydb.cursor()
    tokenizer, model = load_model_embeddings()
    
    i = 1
    for doc in documents:   
        summary = doc["summary"]

        query_summary = "INSERT INTO Summary (id, summary) VALUES (%(id)s, %(summary)s)"
        data_summary = {
            "id": None,
            "summary": summary
        }

        mycursor.execute(query_summary, data_summary)
        # mydb.commit()

        query_metadata = "INSERT INTO Metadata (category, sub_category, url, title, summary_id, date_published) VALUES (%(category)s, %(sub_category)s, %(url)s, %(title)s, %(summary_id)s, %(date_published)s)"
        data_metadata  = {
            "category": "test",
            "sub_category": "test",
            "url" : doc['url'] ,
            "title": doc['pagename'],
            "summary_id" :None,
            "date_published": doc["date"]
        }
        mycursor.execute(query_metadata, data_metadata)
        # mydb.commit()
       
        query_embeddings = "INSERT INTO Embeddings (summary_id, vector) VALUES (%(summary_id)s, %(vector)s)"
        data_embeddings = {
            "summary_id": None,
            "vector": str(create_embedding(tokenizer, model, summary)[0].numpy().dumps())
        }
        mycursor.execute(query_embeddings, data_embeddings)

        mydb.commit()

        i+= 1
        wait = input("Press Enter to continue.")
    mydb.close() 
  
# CREATE TABLE summary (
#     id int NOT NULL AUTO_INCREMENT,
#     summary TEXT (65535) NOT NULL,
#     PRIMARY KEY (id)
# ); 
# CREATE TABLE metadata (
#     category VARCHAR(255) NOT NULL,
#     sub_category VARCHAR(255) NOT NULL,
#     url VARCHAR (255) NOT NULL,
#     title VARCHAR (255) NOT NULL,
#     summary_id int NOT NULL,
#     date_published date,
#     FOREIGN KEY (summary_id) REFERENCES  Summary(id)
# ); 


# CREATE TABLE embeddings (
#     summary_id int NOT NULL,
#     vector BLOB (65535) NOT NULL,
#     FOREIGN KEY (summary_id) REFERENCES  Summary(id)
# ); 