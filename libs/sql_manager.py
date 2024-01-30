import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy import text
import mysql.connector
from libs.embeddings import create_embedding
from libs.embeddings import load_model_embeddings
from sqlalchemy import create_engine
from sqlalchemy import text


def write_to_sql(doc):

    mydb = mysql.connector.connect(
        host="localhost",
        user="junaid",
        password="junaid",
        database="rss_feeds",
        auth_plugin='mysql_native_password'
    )

    mycursor = mydb.cursor()
    tokenizer, model = load_model_embeddings()

 
    summary = doc["summary"]
    category = doc['category']

    query_summary = "INSERT INTO Summary (id, summary) VALUES (%(id)s, %(summary)s)"
    data_summary = {
        "id": None,
        "summary": summary
    }

    mycursor.execute(query_summary, data_summary)
    # mydb.commit()

    #TODO include super_category somehow eventually
    query_metadata = ("INSERT INTO Metadata (category,     url,    title,     summary_id,      date_published)" 
                                 "VALUES (%(category)s,  %(url)s, %(title)s, %(summary_id)s, %(date_published)s)")
    data_metadata  = {
        "category": category,
        "url" : doc['url'] ,
        "title": doc['pagename'],
        "summary_id" :None,
        "date_published": doc["date"]
    }
    mycursor.execute(query_metadata, data_metadata)
    # mydb.commit()
    
    query_embeddings = ("INSERT INTO Embeddings (summary_id,     summary_vector,     category_vector) " 
                                     " VALUES (%(summary_id)s, %(summary_vector)s, %(category_vector)s)")
    data_embeddings = {
        "summary_id": None,
        "summary_vector": str(create_embedding(tokenizer, model, summary)[0].numpy().dumps()),
        "category_vector": str(create_embedding(tokenizer, model, category)[0].numpy().dumps())
    }
    mycursor.execute(query_embeddings, data_embeddings)
    
    
    query_categories = ("INSERT INTO categories (category,     category_vector) " 
                                     " VALUES (%(category)s, %(category_vector)s)")
    data_categories = {
        "category": category,
        "category_vector": str(create_embedding(tokenizer, model, category)[0].numpy().dumps())
    }
    mycursor.execute(query_categories, data_categories)


    mycursor.closer()
    mydb.commit()
    mydb.close() 



    return True

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

    

    def connect(self):
        self.mycursor = self.mydb.cursor()
    

    def connect_sqlalchemy(self):
        con = f'mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}'
        engine = create_engine(
            con, 
            pool_recycle=3600)
        
        return engine
    

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
    
    def sql_to_pandas(self, table_name):
        output = pd.read_sql_table(table_name, 
                                   con=self.connect_sqlalchemy())

        if "index" in output.keys():
            output = output.drop(["index"], axis = 1)

        if "level_0" in output.keys():
            output = output.drop(["level_0"], axis = 1)

        
        return output
    
    def insert_metadata(self, category, url, title, date):
        query = ("INSERT INTO Metadata (category,      url,     title,     summary_id,     date_published)" 
                             "VALUES (%(category)s,  %(url)s, %(title)s, %(summary_id)s, %(date_published)s)")
        data  = {
                  "category": category,
                      "url" : url,
                     "title": title,
               "summary_id" : None,
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


        



    