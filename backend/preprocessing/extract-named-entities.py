import json
import sys
from backend.preprocessing.common import read_dataset
import spacy

# Note: we use the small model because it scores comparably on Named Entities.
nlp = spacy.load('en_core_web_sm')

# Extracts the top 5 entities by frequency.
# NOTE: we use top-5-by-frequency as a proxy for importance.
# A better technique might be something like topic modeling.
def _extract(summary, N=5):
    doc = nlp(summary)
    counts = {}
    for entity in doc.ents:
        print("%s: %s" % (entity.label_, entity.text))
        if entity.text not in counts:
            counts[entity.text] = 1
        else:
            counts[entity.text] += 1
    entites_sorted_by_frequency = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return entites_sorted_by_frequency[:N]


def extract_entities(summaries):
    extracted = []
    for summary in summaries:
        extracted.append(_extract(summary))
    return extracted

def process(summaries, out="entities.json"):
    entities = extract_entities(summaries)
    with open(out, "w") as f:
        json.dump({"entities": entities}, f)

if __name__ == '__main__':
    dataset = read_dataset(sys.argv[1])
    process(dataset[:3])