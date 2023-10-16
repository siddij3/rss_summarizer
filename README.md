﻿# rss_summarizer

- Takes RSS feeds, and scrapes articles using BeautifulSoup; Cleans the articles (HTML, json) and then OpenAI to eliminate having to tailor code for every single host website
- Uses REST APIs to identify which pages can be scraped and which can't be scraped
- OpenAI used to summarize large articles
- Creates embeddings using local sentence embedder, converting sentences into tokens
- Token embeddings are upserted to pinecone to create vector database of trends in AI, Tech, Privacy, and Cybersecurity
