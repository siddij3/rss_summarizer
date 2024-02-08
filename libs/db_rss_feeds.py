
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import mysql.connector
import numpy.typing as npt
from libs.sql_manager import SQLManager

# This would have all the text, names, db details
class RSSDatabase:

    def __init__(self,
                host="localhost",
                user="junaid",
                password="junaid",
                database="rss_feeds",
                auth_plugin='mysql_native_password',
                mydb=None):
        
        self.sqlmanager = SQLManager(host=host,
                user=user,
                password=password,
                database=database,
                auth_plugin=auth_plugin,
                mydb=None)

 
    def query_article_links(self):
        query = ("SELECT url, count(url) AS count FROM metadata GROUP by url;")
        existing_links = [link[0] for link in self.sqlmanager.get_query(query)]
        return existing_links

    def query_article_titles(self):
        query = ("SELECT title, count(title) AS count FROM metadata GROUP by title;")
        existing_titles = [title[0] for title in self.sqlmanager.get_query(query)]
        return existing_titles
    
    def commit(self):
        self.sqlmanager.commit()

    def end_connection(self):
        self.sqlmanager.end_connection()

    def insert_article_entry(self, summary, summary_vector, 
                                   category, category_vector, 
                                   url,      title, 
                                   author,   date):
        query = ("INSERT INTO Summary (id,     summary) "
                           " VALUES (%(id)s, %(summary)s)")
        data = {
                 "id": None,
            "summary": summary
        }
        self.sqlmanager.execute_insert_query(query, data)


        query = ("INSERT INTO Metadata (category,      url,     title,     summary_id,     author,      date_published)" 
                             "VALUES (%(category)s,  %(url)s, %(title)s, %(summary_id)s,  %(author)s, %(date_published)s)")
        data  = {
                  "category": category,
                      "url" : url,
                     "title": title,
               "summary_id" : None,
               "author": author, 
            "date_published": date
        }
        print(data)
        self.sqlmanager.execute_insert_query(query, data)

        query = ("INSERT INTO Embeddings (summary_id,     summary_vector,     category_vector) " 
                              " VALUES (%(summary_id)s, %(summary_vector)s, %(category_vector)s)")
        data = {
                "summary_id": None,
             "summary_vector": summary_vector,
            "category_vector": category_vector
        }
        self.sqlmanager.execute_insert_query(query, data)
    

        query = ("INSERT INTO categories (category,     category_vector) " 
                              " VALUES (%(category)s, %(category_vector)s)")
        data = {
                   "category": category,
            "category_vector": category_vector
        }
        self.sqlmanager.execute_insert_query(query, data)