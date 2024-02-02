from libs.hyperdb import HyperDB
import json
import pickle

import numpy as np
import api
import sys
np.set_printoptions(threshold=sys.maxsize)
from libs.sql_manager import SQLManager
import pandas as pd


if __name__ == "__main__":

  
    # THis queries DB 
    sql_manager = SQLManager()
    sql_manager.cursor()

    # For removing duplicate links TODO
    embeddings = sql_manager.sql_to_pandas("embeddings")
    summary = sql_manager.sql_to_pandas("summary")
    metadata = sql_manager.sql_to_pandas("metadata")
    category = sql_manager.sql_to_pandas("categories")

    embeddings["summary_vector"] = embeddings.apply(lambda row: pickle.loads(row["summary_vector"]), axis=1)
    embeddings["category_vector"] = embeddings.apply(lambda row: pickle.loads(row["category_vector"]), axis=1)
    
    metadata_list = [metadata.loc[i, :].values.flatten().tolist() for i in range(embeddings.shape[0])]

    
    tmp = embeddings["summary_vector"].tolist() 
    vectors_summaries = None
    for vector in tmp:
        if vectors_summaries is None:
                    vectors_summaries = np.empty((0, len(vector)), dtype=np.float32)
        vectors_summaries = np.vstack([vectors_summaries, vector]).astype(np.float32)

    tmp = embeddings["category_vector"].tolist()
    vectors_categories = None
    for vector in tmp:
        if vectors_categories is None:
                    vectors_categories = np.empty((0, len(vector)), dtype=np.float32)
        vectors_categories = np.vstack([vectors_categories, vector]).astype(np.float32)

    db_summaries = HyperDB(documents = summary["summary"].tolist(), vectors = vectors_summaries, metadata=metadata_list )
    db_categories = HyperDB(documents = summary["summary"].tolist(), vectors = vectors_categories, metadata=metadata_list )
    
    results_sum = db_summaries.query("Google.", top_k=8)
    results_cat = db_categories.query("Google.", top_k=8)

    for result in results_sum:
           print(result[0])

    print('\n\n')
    for result in results_cat:
        print(result[0])
 