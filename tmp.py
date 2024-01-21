from hyperdb import HyperDB
import json

import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)
from libs.libs import get_links
from libs.libs import filter_page
from libs.libs import get_page
from libs.libs import REST_codes
from libs.libs import get_with_header
from datetime import datetime

from bs4 import BeautifulSoup

url = f"https://api.start.me/widgets/64657916,64619065,64814145/articles" 
url2 = f"https://api.start.me/widgets/63871721/articles"
technology_list = ["AI", "Technology", "Privacy", "Cybersecurity"]


if __name__ == "__main__":

   url = ["https://blog.google/technology/safety-security/google-account-recover/",
          "http://arxiv.org/abs/2312.06008"]

   documents = []
   with open("summaries.txt", "r") as f:
      for line in f:
         documents.append(json.loads(line))


   duplicates  = [x for x in documents if x["url"] in url]

   for link in duplicates:
      print(link['url'])
      url.remove(link['url'])

   print(url)