from hyperdb import HyperDB
import json

if __name__ == "__main__":

    documents = a
    key = None
    MAX_BATCH_SIZE = 2048  # OpenAI batch endpoint max size https://github.com/openai/openai-python/blob/main/openai/embeddings_utils.py#L43

    if isinstance(documents, list):
        if isinstance(documents[0], dict):
            texts = []
            if isinstance(key, str):
                if "." in key:
                    key_chain = key.split(".")
                else:
                    key_chain = [key]
                for doc in documents:
                    for key in key_chain:
                        doc = doc[key]
                    texts.append(doc.replace("\n", " "))
            elif key is None:
                for doc in documents:
                    text = ", ".join([f"{key}: {value}" for key, value in doc.items()])
                    texts.append(text)
        elif isinstance(documents[0], str):
            texts = documents
    batches = [
        texts[i : i + MAX_BATCH_SIZE] for i in range(0, len(texts), MAX_BATCH_SIZE)
    ]
    embeddings = []
    for batch in batches:
        print(batch)
    pass