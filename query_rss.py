import json
from hyperdb import HyperDB
import api

if __name__ == '__main__':

    documents = []
    
    pokemon = 'pokemon.jsonl'
    poke_key = "info.description"

    mine = 'summaries.txt'
    mine_keys = "summary"
    with open(mine, "r") as f:
        for line in f:
            documents.append(json.loads(line))

    
    
    db = HyperDB(documents, key=mine_keys)
    # print(db)
    db.save("rss_articles.pickle.gz")


    db.load("rss_articles.pickle.gz")


    results = db.query("sleep.", top_k=5)

    print(results)
