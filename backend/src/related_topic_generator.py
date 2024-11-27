import json
from openai import OpenAI
import networkx as nx

# A  class to generate related topics for a given query.
# NOTE: we use a class here since we could imagine e.g., caching or other optimizations.
# We aren't doing them currently, but a class still makes sense.
# `topics` are the topics from our set of summaries. We'll use GPT to identify which
# are probably most relevant to the query.
class RelatedTopicGenerator:
    def __init__(self, client: OpenAI, topics, entities):
        self.client = client
        self.topics = topics
        self.entities = entities

    def _construct_prompt(self, query, answer):
        context = "\n".join(self.topics + self.entities)
        return f"""
        Given the question: {query}

        And the answer: {answer}

        What topics or entities might be relevant? Pick the best 2-5 from this list:
        {context}

        Give your answer as a JSON list.
        """

    def generate(self, query, answer):
        prompt = self._construct_prompt(query, answer)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        parsed = json.loads(response.choices[0].message.content.strip("```json\n").strip("```").lower())
        return parsed
    
def topic_generator_for_entity_graph(G: nx.Graph) -> RelatedTopicGenerator:
    # Get the topics out of the entity graph.
    topics = [node[0] for node in G.nodes.items() if node[1]['type'] == 'TOPIC']
    entities = [node[0] for node in G.nodes.items() if node[1]['type'] == 'ENTITY']
    return RelatedTopicGenerator(OpenAI(), topics, entities)