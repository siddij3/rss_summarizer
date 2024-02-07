import gzip
import pickle
import numpy as np

MAX_BATCH_SIZE = 2048    
from transformers import AutoTokenizer, AutoModel
import torch
torch.set_printoptions(profile="full")
import torch.nn.functional as F
import tiktoken
import re

import nltk
nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
nltk.download('stopwords')
from nltk.corpus import stopwords

from libs.vector_math import (
    dot_product,
    adams_similarity,
    cosine_similarity,
    derridaean_similarity,
    euclidean_metric,
    hyper_SVM_ranking_algorithm_sort,
)

class HyperDB:
    def __init__(
        self,
        documents=None,
        vectors=None,
        metadata=None,
        key=None,
        model=None,
        similarity_metric="cosine",
    ):
        documents = documents or []
        self.documents = []
        self.vectors = None
        if vectors is not None:
            self.vectors = vectors
            self.documents = documents
            self.metadata = metadata
        # else:
        #     self.add_documents(documents)

        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')

        if model is not None:
            self.model = model
        else:
            self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')


        if similarity_metric.__contains__("dot"):
            self.similarity_metric = dot_product
        elif similarity_metric.__contains__("cosine"):
            self.similarity_metric = cosine_similarity
        elif similarity_metric.__contains__("euclidean"):
            self.similarity_metric = euclidean_metric
        elif similarity_metric.__contains__("derrida"):
            self.similarity_metric = derridaean_similarity
        elif similarity_metric.__contains__("adams"):
            self.similarity_metric = adams_similarity
        else:
            raise Exception(
                "Similarity metric not supported. Please use either 'dot', 'cosine', 'euclidean', 'adams', or 'derrida'."
            )

    def dict(self, vectors=False):
        if vectors:
            return [
                {"document": document, "vector": vector.tolist(), "metadata": metadata.tolist(), "index": index}
                for index, (document, metadata, vector) in enumerate(
                    zip(self.documents, self.metadata, self.vectors)
                )
            ]
        return [
            {"document": document,  "index": index}
            for index, document in enumerate(self.documents)
        ]

    # def add(self, documents, vectors=None):
    #     if not isinstance(documents, list):
    #         return self.add_document(documents, vectors)
    #     self.add_documents(documents, vectors)

    # def add_document(self, document: dict, vector=None):
    #     vector = (
    #         vector if vector is not None else self.embedding_function([document])[0]
    #     )
    #     if self.vectors is None:
    #         self.vectors = np.empty((0, len(vector)), dtype=np.float32)
    #     elif len(vector) != self.vectors.shape[1]:
    #         raise ValueError("All vectors must have the same length.")
    #     self.vectors = np.vstack([self.vectors, vector]).astype(np.float32)
    #     self.documents.append(document)

    def remove_document(self, index):
        self.vectors = np.delete(self.vectors, index, axis=0)
        self.documents.pop(index)
        #TODO remove from SQL server as well

    # def add_documents(self, documents, vectors=None):
    #     if not documents:
    #         return

    #     for vector, document in zip(vectors, documents):
    #         self.add_document(document, vector)

    def save(self, storage_file):
        data = {"vectors": self.vectors, "documents": self.documents}
        if storage_file.endswith(".gz"):
            with gzip.open(storage_file, "wb") as f:
                pickle.dump(data, f)
        else:
            with open(storage_file, "wb") as f:
                pickle.dump(data, f)

    def load_vector(self, data):

        self.vectors = data["vectors"]
        self.metadata = data["metadata"]
        self.documents = data["documents"]

    def query(self, query_text, top_k=5, return_similarities=True):
        query_vector = self.embedding_function([query_text])[0]

        # print(query_vector)
        # print(type(self.vectors[0]))
        #  print((self.vectors.shape)) This should give (# elemnets, # dimensions in array)
        #  Vectors is of type ndarray with ndarry elements
        ranked_results, similarities = hyper_SVM_ranking_algorithm_sort(
            self.vectors, query_vector, top_k=top_k, metric=self.similarity_metric
        )
        if return_similarities:
            return list(
                zip([(self.documents[index], self.metadata[index] ) for index in ranked_results], similarities)
            )
        return [(self.documents[index], self.metadata[index]) for index in ranked_results]
    

    def embedding_function(self, sentence):

        # Tokenize sentences
        encoded_input = self.tokenizer(sentence, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform pooling
        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings
    
    
def num_tokens_from_string(page_string, model) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(page_string))
    return num_tokens


#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def load_model_embeddings():
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')

    return tokenizer, model

def create_embedding(tokenizer, model, sentences):
    # sentences = process_text(sentences)
    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

    return sentence_embeddings



def process_text(text):
    # Make all the strings lowercase and remove non alphabetic characters
    text = re.sub('[^A-Za-z]', ' ', text.lower())

    # Tokenize the text; this is, separate every sentence into a list of words
    # Since the text is already split into sentences you don't have to call sent_tokenize
    tokenized_text = word_tokenize(text)

    # Remove the stopwords and stem each word to its root
    clean_text = [
        stemmer.stem(word) for word in tokenized_text
        if word not in stopwords.words('english')
    ]

    # Remember, this final output is a list of words
    return clean_text