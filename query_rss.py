import json
from hyperdb import HyperDB


if __name__ == '__main__':

    documents = []
    with open("summaries.txt", "r") as f:
        for line in f:
            documents.append(json.loads(line))

    db = HyperDB(documents, key="summary")

    db.save("demo/rss_articles.pickle.gz")


    db.load("demo/rss_articles.pickle.gz")


    results = db.query("Markov.", top_k=5)

    print(results)
