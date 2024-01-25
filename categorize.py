
from bertopic import BERTopic
import collections
from tqdm import tqdm
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from sqlalchemy import insert


if __name__ == '__main__':

    topic_model = BERTopic.load("MaartenGr/BERTopic_ArXiv")

    topic_model.get_topic_info()

    docs = 1 #extract the summary texts here


    # Create embeddings 
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(docs, show_progress_bar=True)

    embeddings = np.load('/content/drive/MyDrive/embeddings.npy') # from vector database??

    # Extract vocab to be used in BERTopic
    vocab = collections.Counter() # returns a dictionary object, so vocab might be a word counter
    tokenizer = CountVectorizer().build_tokenizer()
    for doc in tqdm(docs):
    vocab.update(tokenizer(doc))
    vocab = [word for word, frequency in vocab.items() if frequency >= 15]; len(vocab)

    

    # model = "gpt-3.5-turbo-16k"

    # documents = []
    # with open("summaries.txt", "r") as f:
    #     for line in f:
    #         documents.append(json.loads(line))


    # docs = []
    # for doc in documents:
    #     docs.append(doc[ "pagename"] )


    # sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    # embeddings = sentence_model.encode(docs, show_progress_bar=False)
    # stopwords = list(stopwords.words('english')) + ['http', 'https', 'amp', 'com']

    # vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english")
    # # topic_model = BERTopic.load("MaartenGr/BERTopic_ArXiv")
    # model = BERTopic(
    #     vectorizer_model=vectorizer_model,
    #     language='english', calculate_probabilities=True,
    #     verbose=True
    # )

    # topics, probs = model.fit_transform(docs)

    # freq = model.get_topic_info()
    # freq.head(10)
    # model.visualize_topics()
   

    # # model = BERTopic(verbose=True)
    # # model.fit(docs)
    # # topics, probabilities = model.transform(docs)
    # # model.get_topic(2)
    # # model.get_topic_freq().head(10)
    # # model.visualize_topics()
    # # model.visualize_barchart()
    # # model.visualize_heatmap()

    # # wait = input("Press Enter to continue.")


    # #https://huggingface.co/davanstrien/chat_topics
    # #https://huggingface.co/cristian-popa/bart-tl-all, https://github.com/CristianViorelPopa/BART-TL-topic-label-generation

    # # metadata = get_metadata(model, documents)

    # docs = df[0:10000].text.to_list()
    # docs
