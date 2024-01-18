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

    url = "https://www.marktechpost.com/2024/01/06/this-ai-paper-presents-a-comprehensive-study-of-knowledge-editing-for-large-language-models/"


    with open('summaries.txt') as f:
      json_data = json.load(f)
      print(json_data)