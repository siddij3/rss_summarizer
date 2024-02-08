
from transformers import AutoTokenizer, AutoModel
import torch
torch.set_printoptions(profile="full")
import warnings
warnings.filterwarnings('ignore', category=UserWarning, message='TypedStorage is deprecated')
import torch.nn.functional as F
import tiktoken
import re

from transformers import AutoTokenizer, AutoModel
import numpy as np

import openai

from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


from libs.vector_math import (
    dot_product,
    adams_similarity,
    cosine_similarity,
    derridaean_similarity,
    euclidean_metric,
    hyper_SVM_ranking_algorithm_sort,
)

    
class Tokens():
    def __init__(
            self, 
            auto_tokenizer='sentence-transformers/all-MiniLM-L12-v2', 
            auto_model='sentence-transformers/all-MiniLM-L12-v2'
        ):
        
        super().__init__()
        # Load model from HuggingFace Hub

        self.auto_tokenizer = AutoTokenizer.from_pretrained(auto_tokenizer)
        self.auto_model = AutoModel.from_pretrained(auto_model)

        self.stemmer = PorterStemmer()

    def create_embedding(self):

        pass

    def num_tokens_from_string(self, text) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self.auto_model)
        num_tokens = len(encoding.encode(text))
        return num_tokens
    

    def create_embedding(self, sentences):
        def mean_pooling(model_output, attention_mask):
            token_embeddings = model_output[0] #First element of model_output contains all token embeddings
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        

        # Tokenize sentences
        encoded_input = self.auto_tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        # sentences = self.process_text(sentences)
        # Tokenize sentences
        with torch.no_grad():
            model_output = self.auto_model(**encoded_input)

        # Perform pooling
        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings


    
    def process_text(self, text):
        # Make all the strings lowercase and remove non alphabetic characters
        text = re.sub('[^A-Za-z]', ' ', text.lower())

        # Tokenize the text; this is, separate every sentence into a list of words
        # Since the text is already split into sentences you don't have to call sent_tokenize
        tokenized_text = self.create_embedding(text)

        # Remove the stopwords and stem each word to its root
        clean_text = [
            self.stemmer.stem(word) for word in tokenized_text
            if word not in stopwords.words('english')
        ]

        # Remember, this final output is a list of words
        return clean_text
    

class HyperDB():
    def __init__(
        self,
        documents=None,
        vectors=None,
        metadata=None,
        key=None,
        model=None,
        similarity_metric="cosine",
        auto_tokenizer='sentence-transformers/all-MiniLM-L12-v2',  #Clean these up 
        auto_model='sentence-transformers/all-MiniLM-L12-v2'
        ):

        super().__init__()
        
        documents = documents or []
        self.documents = []
        self.vectors = None
        
        if vectors is not None:
            self.vectors = vectors
            self.documents = documents
            self.metadata = metadata
        # else:
        #     self.add_documents(documents)

        self.tokenizer = AutoTokenizer.from_pretrained(auto_tokenizer)

        if model is not None:
            self.model = model
        else:
            self.model = AutoModel.from_pretrained(auto_model)


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


# TODO We can later fine-tune based on the data we get
class ChatBotHandler():
    def __init__(self,
                 chatbot_model="gpt-3.5-turbo-16k"
                 ):
        super().__init__()

        self.chatbot_model = chatbot_model

        self.reponses = []


    def message_maker(self, command, message_content):
        
        message = [{"role": "system", "content": command},
                   {"role": "user", "content": message_content}]
        
        response = openai.ChatCompletion.create(
                    model=self.chatbot_model,
                    messages=message
                )
        
        self.reponses.append(response)
        return response.choices

    def response_logger():
        """
        {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo-0613",
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [{
            "index": 0,
            "message": {
            "role": "assistant",
            "content": "\n\nHello there, how may I assist you today?",
            },
            "logprobs": null,
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
        }"""
        pass
