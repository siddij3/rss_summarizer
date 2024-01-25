from hyperdb import HyperDB
import json

import numpy as np
import api
import sys
np.set_printoptions(threshold=sys.maxsize)
from libs.site_handler import get_links
from libs.site_handler import filter_page
from libs.site_handler import get_page
from libs.site_handler import REST_codes
from libs.site_handler import get_with_header
from datetime import datetime

from bs4 import BeautifulSoup

url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"
technology_list = ["AI", "Technology", "Privacy", "Cybersecurity"]
model = "gpt-3.5-turbo-16k"


if __name__ == "__main__":
    documents = []
    with open("summaries.txt", "r") as f:
        for line in f:
            documents.append(json.loads(line))

    db = HyperDB(documents, key="summary")
    db.save("demo/rss_articles.pickle.gz")
    db.load("demo/rss_articles.pickle.gz")
    results = db.query("Markov.", top_k=5)