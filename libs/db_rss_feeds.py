
import numpy.typing as npt
from libs.sql_manager import SQLManager
from libs.credentials import get_db_creds
# Need to do this better somehow


class RSSDatabase:

    def __init__(self,
                mydb=None):

        creds = get_db_creds()

        self.sqlmanager = SQLManager(
                            host=creds["host"],
                            user=creds["user"],
                            password=creds["password"],
                            database=creds["database"],
                            auth_plugin=creds["auth_plugin"],
                            mydb=None)

 
    def query_article_links(self):
        query = ("SELECT url, count(url) AS count FROM metadata GROUP by url;")
        existing_links = [link[0] for link in self.sqlmanager.get_query(query)]
        return existing_links

    def query_article_titles(self):
        query = ("SELECT title, count(title) AS count FROM metadata GROUP by title order by count Desc;")
        existing_titles = [title[0] for title in self.sqlmanager.get_query(query)]
        return existing_titles
    
    def query_categories(self):
        query = ("SELECT category, count(category) AS count FROM metadata GROUP by category order by count Desc;")
        categories = [category for category in self.sqlmanager.get_query(query)]
        return categories
    
    def query_table_all_rows(self, table):
        query = (f"SELECT * FROM {table};")
        rows = [item for item in self.sqlmanager.get_query(query)]
        return rows

    def commit(self):
        self.sqlmanager.commit()

    def end_connection(self):
        self.sqlmanager.end_connection()

    def insert_article_entry(self, summary: str, summary_vector: npt.ArrayLike, 
                                   category: str, category_vector: npt.ArrayLike, 
                                   url: str,      title: str, 
                                   author: str,   date) -> None:
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