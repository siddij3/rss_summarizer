from transformers import AutoTokenizer, AutoModel
import torch
torch.set_printoptions(profile="full")
import torch.nn.functional as F
import tiktoken

import json

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

def create_embedding(sentences):
    tokenizer, model = load_model_embeddings()

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


def write_to_file(dictionary):
    with open("summaries.txt", "a") as outfile:
        outfile.write(json.dumps(dictionary))
        outfile.write('\n')
    