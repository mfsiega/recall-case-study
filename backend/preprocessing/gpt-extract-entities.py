import re
import sys
from openai import OpenAI
import json

from backend.preprocessing.common import read_dataset

# Reads the API key from env var OPENAI_API_KEY by default.
client = OpenAI()

def generate_entities(summaries):
    entities = []
    i = 0
    for text in summaries:
        prompt = f"""
        Take the following document and extract the 5-10 most important entities, topics, and concepts. Present the entities as a JSON object structured as: {{ name: "Mitochondrial health", description: "example description", related_topics: ["longevity", "stress"]}}.

        {text}
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            parsed = json.loads(response.choices[0].message.content.strip("```json\n").strip("```").lower())
            entities.append({i: parsed})
            print("Processed summary %d" % i)
        except Exception as e:
            print("Failed to generate entities for summary %d" % i)
            print(e)
            entities.append({i: []})
        i += 1
    return entities

# Generate and save embeddings
def process(summaries, out="entities.json"):
    entities = generate_entities(summaries)
    with open(out, "w") as f:
        json.dump({"entities": entities}, f)

if __name__ == '__main__':
    # Read the dataset.
    dataset = read_dataset(sys.argv[1])
    process(dataset)