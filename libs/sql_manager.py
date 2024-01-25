import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy import text

def get_creds_local():
    server = 'localhost' 
    database = 'rss_feeds' 
    username = 'junaid' 
    password = 'junaid'  
    port = 3306

    con = f'mysql+pymysql://{username}:{password}@{server}/{database}'
    return con

def connect():
    engine = create_engine(
            get_creds_local(), 
            pool_recycle=3600)
    return engine

# def summary_table():
#     return "stock_indexes"

# def quotes_table():
#     return "quotes"

def insert_item(query, engine, table):

    with engine.begin() as conn:
        try:
            result = conn.execute(query)
        except:
            return False 
        
    return result

def check_tables(engine, table):
    isTable = False

    query = text(f"SELECT * FROM {table}")

    with engine.begin() as conn:
        try:
            result = conn.execute(query)
        except:
            return isTable 
        
    isTable = True
    return result

def remove_table(table, engine):
    query = text(f"Drop table {table}")
    with engine.begin() as conn:
        try:
            result = conn.execute(query)
        except:
            return False


def pandas_to_sql(table_name, pandas_dataset, engine):
    return pandas_dataset.to_sql(table_name, con=engine)
    
def pandas_to_sql_if_exists(table_name, pandas_dataset, engine,  action):
    return pandas_dataset.to_sql(table_name, con=engine, if_exists=action, index=False)


def sql_to_pandas(table_name, engine):
    output = pd.read_sql_table(table_name, con=engine.connect())
    try:
        output = output.drop(["index"], axis = 1)
        print(f"'index' parameter dropped {table_name}");
    except:
        print("'index' parameter does not exist");
    
    try:
        output = output.drop(["level_0"], axis = 1)
        print("'level_0' parameter dropped");
    except:
        print("'level_0' parameter does not exist");
    
    return output

def get_query_to_pandas(engine, query):
    with engine.begin() as conn:
            result = conn.execute(query)

    output = pd.DataFrame()
    for r in result:

        df_dictionary = pd.DataFrame([r._asdict()])
        output = pd.concat([output, df_dictionary], ignore_index=True)

    try:
        output = output.drop(["index"], axis = 1)
    except:
        pass
    
    try:
        output = output.drop(["level_0"], axis = 1)
    except:
        pass
    
    return output
