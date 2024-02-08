import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import mysql.connector

#This is the blind messenger
class SQLManager:
    def __init__(self,host=None,
                user=None,
                password=None,
                database=None,
                auth_plugin=None,
                mydb=None):
        
        self.host = host
        self.user=user
        self.password=password
        self.database=database
        self.auth_plugin=auth_plugin

        if mydb == None:
            self.mydb = mysql.connector.connect(
                    host=  host,
                    user= user,
                    password= password,
                    database= database,
                    auth_plugin= auth_plugin
                    )
        else:
            self.mydb = mydb

        self.mycursor = self.mydb.cursor()

    @property
    def cursor(self):
        return self.mycursor
    
    def commit(self):
        self.mydb.commit()

    def end_connection(self):
        self.mycursor.close()
        self.mydb.close()


    def connect_sqlalchemy(self):
        self.con = f'mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}'
        self.engine = create_engine(
            self.con, 
            pool_recycle=3600)
        return self.con
    
    def execute_insert_query(self, query, data):
        self.mycursor.execute(query, data)


    def query_tables(self, table):
        # Assuming that there's a table with that name apriori
        query = text(f"SELECT * FROM {table}")
        with self.connect_sqlalchemy().begin() as conn:
            result = conn.execute(query)
        return result
    
    def get_query(self, query):
        self.mycursor.execute(query)
        return self.mycursor
    
    def sql_to_pandas(self, table_name):
        output = pd.read_sql_table(table_name, 
                                   con=self.connect_sqlalchemy())
        
        return output
    