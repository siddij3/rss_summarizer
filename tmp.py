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
    rss_all = get_links([url, url2])

    forbidden_links = []
    filtered_links = []
    url = "https://www.marktechpost.com/2024/01/06/this-ai-paper-presents-a-comprehensive-study-of-knowledge-editing-for-large-language-models/"

    page = get_page(url)  

    if not REST_codes(page.status_code):
       get_with_header(url)



    print(page.text)


    # soup = BeautifulSoup(page.text, 'html.parser')

    # print(soup)
    # # for i, theme in enumerate(rss_all):
    #     for entry in rss_all[theme]:
            
    #         date = datetime.today().strftime('%Y-%m-%d')

    #         url = entry['url']
    #         metadata = {"category": technology_list[i], "url": url, "pagename": entry['title'], "date": date}

    #         if filter_page(url):
    #             filtered_links.append(url) 
    #         else:
    #             continue

    #         page = get_page(url)
    #         if page.status_code == 403 :
    #             forbidden_links.append(url)
    #             continue



