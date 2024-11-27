import sys
from openai import OpenAI
import numpy as np
import json

# Reads the API key from env var OPENAI_API_KEY by default.
client = OpenAI()

# Dataset: A list of Markdown-formatted summaries
def read_dataset(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to generate embeddings for a list of texts
def generate_embeddings(texts):
    embeddings = []
    i = 0
    for text in texts:
        try:
            response: OpenAI.CreateEmbeddingResponse = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embeddings.append(response.data[0].embedding)
            print("Processed embedding %d" % i)
        except Exception as e:
            print("Failed to generate embeddings for summary %d" % i)
            print(e)
            # We generate a fake embedding in the right shape. This is a shortcut
            # to make the rest of the processing work as expected. These summaries
            # will effectively be excluded from semantic search.
            # TODO: handle these cases properly.
            embeddings.append([0]*len(embeddings[-1]))
        i += 1

    return embeddings

# Generate and save embeddings
def process(summaries):
    embeddings = generate_embeddings(summaries)
    with open("embeddings.json", "w") as f:
        json.dump({"embeddings": embeddings}, f)

if __name__ == '__main__':
    dataset = read_dataset(sys.argv[1])
    process(dataset)