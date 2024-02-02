
import json
import api

import libs.site_handler as site_handler

from libs.embeddings import create_embedding
from libs.embeddings import load_model_embeddings
# from langchain_community.vectorstores import Chroma
# from langchain_community.document_loaders import TextLoader

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
               
    
    # with open("summaries.txt", "r") as f:
    #     for line in f:
    #         documents.append(json.loads(line))

    # sql_manager.insert_summary(tmp["summary"])
    # sql_manager.insert_metadata(tmp["category"], tmp["url"], tmp["title"], tmp["date"])
    # sql_manager.commit()  