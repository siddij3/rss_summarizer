
import json
import api

import libs.site_handler as site_handler



TF_ENABLE_ONEDNN_OPTS=0



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


 
    # with open("summaries.txt", "r") as f:
    #     for line in f:
    #         documents.append(json.loads(line))

    # sql_manager.insert_summary(tmp["summary"])
    # sql_manager.insert_metadata(tmp["category"], tmp["url"], tmp["title"], tmp["date"])
    # sql_manager.commit()  