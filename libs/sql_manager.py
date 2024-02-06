import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import mysql.connector

class SQLManager:
    def __init__(   self,
                    host="localhost",
                    user="junaid",
                    password="junaid",
                    database="rss_feeds",
                    auth_plugin='mysql_native_password',
                    mydb=None):
                
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.auth_plugin = auth_plugin
        self.port = 3306
        
        self.mydb = mysql.connector.connect(
                host=  self.host,
                user= self.user,
                password= self.password,
                database= self.database,
                auth_plugin=self.auth_plugin
                )

        self.mycursor = self.mydb.cursor()

    @property
    def cursor(self):
        return self.mycursor

    def end_connection(self):
        self.mycursor.close()
        self.mydb.close()

    def cursor(self):
        return self.mycursor

    def commit(self):
        self.mydb.commit()
        # self.mycursor.close()

    def connect_sqlalchemy(self):
        self.con = f'mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}'
        self.engine = create_engine(
            self.con, 
            pool_recycle=3600)
        return self.con
    
    def execute_query(self, query, data=None):
        if data == None:
            self.mycursor.execute(query)
        else:
            self.mycursor.execute(query, data)

    def query_tables(self, table):
        # Assuming that there's a table with that name apriori
        query = text(f"SELECT * FROM {table}")

        with self.connect_sqlalchemy().begin() as conn:
            result = conn.execute(query)

        return result
    
    def query(self, query):
        self.mycursor.execute(query)
        return self.mycursor
    
    def sql_to_pandas(self, table_name):
        output = pd.read_sql_table(table_name, 
                                   con=self.connect_sqlalchemy())
        
        return output
    
    def insert_metadata(self, category, url, title, author, date):
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
        self.mycursor.execute(query, data)
   
    def insert_summary(self, summary):
        query = ("INSERT INTO Summary (id,     summary) "
                           " VALUES (%(id)s, %(summary)s)")
        data = {
                 "id": None,
            "summary": summary
        }
        self.mycursor.execute(query, data)

    def insert_embedding(self, summary_vector, category_vector):
        query = ("INSERT INTO Embeddings (summary_id,     summary_vector,     category_vector) " 
                              " VALUES (%(summary_id)s, %(summary_vector)s, %(category_vector)s)")
        data = {
                "summary_id": None,
             "summary_vector": summary_vector,
            "category_vector": category_vector
        }
        self.mycursor.execute(query, data)
    

    def insert_category(self, category, category_vector):
        query = ("INSERT INTO categories (category,     category_vector) " 
                              " VALUES (%(category)s, %(category_vector)s)")
        data = {
                   "category": category,
            "category_vector": category_vector
        }
        self.mycursor.execute(query, data)


        



    