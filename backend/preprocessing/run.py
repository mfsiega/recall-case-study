import re
import sys
import time
from openai import OpenAI
import numpy as np
import json
import spacy

# Reads the API key from env var OPENAI_API_KEY by default.
client = OpenAI()
nlp = spacy.load("en_core_web_sm")

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
            embeddings.append([0]*len(embeddings[-1]))
        i += 1

    return embeddings

def generate_entities(texts):
    entities = []
    i = 0
    for text in texts:
        text = " ".join(text.split()[:1500]) # Truncate to avoid token limit. To do this properly, we should actually tokenize it.
        prompt = f"""
        Extract named entities from the following text. Include key topics, terms, concepts, and names. Provide the entities as a comma-separated list.

        Text:
        {text}
        """
        try:
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=100
            )
            print(response)
            entities.append(response.choices[0].text.split("\n")[-1].split(","))
            print("Processed entities %d" % i)
        except Exception as e:
            print("Failed to generate entities for summary %d" % i)
            print(e)
            entities.append([])
        i += 1
    return entities

# Generate and save embeddings
def process(summaries):
    embeddings = generate_embeddings(summaries)
    with open("embeddings.json", "w") as f:
        json.dump({"embeddings": embeddings}, f)
    entities = generate_entities(summaries)
    with open("entities.json", "w") as f:
        json.dump({"entities": entities}, f)

if __name__ == '__main__':
    # Read the dataset.
    dataset = read_dataset(sys.argv[1])
    print("Dataset length=%d" % len(dataset))
    process(dataset)