import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import mysql.connector

def get_db_creds() -> dict:
    creds = {  "host":"localhost",
                "user":"junaid",
                "password":"junaid",
                "database":"rss_feeds",
                "auth_plugin":'mysql_native_password'}
    
    return creds


#This is the blind messenger
class SQLManager:
    def __init__(self,host=None,
                user=None,
                password=None,
                database=None,
                auth_plugin=None,
                mydb=None):
        
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

    def execute_insert_query(self, query, data):
        self.mycursor.execute(query, data)
    
    def get_query(self, query):
        self.mycursor.execute(query)
        return self.mycursor
    
class SQLandPandas:
    def __init__(self) -> None:
        #TODO Abstract this too later
        creds = get_db_creds()
        self.host = creds['host']
        self.user=creds['user']
        self.password=creds['password']
        self.database=creds['database']
        self.auth_plugin=creds['auth_plugin']

        pass

    def connect_sqlalchemy(self):
        self.con = f'mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}'
        self.engine = create_engine(
            self.con, 
            pool_recycle=3600)
        return self.con
    

    def query_tables(self, table):
        # Assuming that there's a table with that name apriori
        query = text(f"SELECT * FROM {table}")
        with self.connect_sqlalchemy().begin() as conn:
            result = conn.execute(query)
        return result
    

    
    def sql_to_df(self, table_name):
        output = pd.read_sql_table(table_name, 
                                   con=self.connect_sqlalchemy())
        
        return output