import json
import re
import sys
import faiss
import numpy as np
from openai import OpenAI
from backend.src import build_entity_graph

class QueryServer:
    def __init__(self, summaries, embeddings, entities, client: OpenAI):
        self.summaries = summaries
        self.embeddings = np.array(embeddings)
        self.entities = entities
        self.client = client
        self.faiss_index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.faiss_index.add(self.embeddings)
        self.entity_graph = build_entity_graph.build_graph(entities)

    def _embeddings_for_query(self, query):
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        return response.data[0].embedding
    
    def _relevant_summary_indices(self, query_embedding, N=3):
        distances, indices = self.faiss_index.search(np.array([query_embedding]), N)
        print(distances)
        print(indices)
        return indices[0]

    def _construct_query_prompt(self, query, relevant_summary_indices):
        relevant_summaries = [self.summaries[index] for index in relevant_summary_indices]
        context = "\n\n".join([f"{i+1}. {summary}" for i, summary in enumerate(relevant_summaries)])
        return f"""
                The user has asked a question. Answer the question, based on the information in the listed summaries provided.

                Keep your answer short, since it's to be read in a chat application.

                Summaries:
                {context}

                User question: {query}

                Answer:
                """
    
    def _generate_answer(self, query_prompt):
        # Call the OpenAI API for a natural language response
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": query_prompt}
            ],
        )
        return response.choices[0].message.content
    
    def _extract_entities(self, answer):
        print(answer)
        match = re.search(r"Key entities:\s*(.+)", answer)
        if match:
            return [entity.lower() for entity in match.group(1).split(", ")[:5]]
        else:
            print("No entities found.")
            return []

    
    def _find_related_summaries(self, entities):
        results = {}
        for entity in entities:
            try:
                results[entity] = []
                for neighbor in self.entity_graph.neighbors(entity):
                    results[entity].append(neighbor)
            except:
                pass
        return results
    
    def _append_related_summaries(self, answer, related_summaries):
        answer += "\n"
        for key, value in related_summaries.items():
            answer += "%s: %s\n" % (key, ", ".join(str(x) for x in value))
        return answer

    def handle_query(self, query):
        # Get the embeddings for the query.
        query_embedding = self._embeddings_for_query(query)

        # Find the relevant summaries.
        relevant_summary_indices = self._relevant_summary_indices(query_embedding)

        # Construct query prompt.
        query_prompt = self._construct_query_prompt(query, relevant_summary_indices)

        # Generate answer.
        answer = self._generate_answer(query_prompt)
        print(answer)

        # Extract entities from answer.
        entities = self._extract_entities(answer)
        print(entities)

        # Find summaries that have the same entities as the answer.
        related_summaries = self._find_related_summaries(entities)
        
        answer = self._append_related_summaries(answer, related_summaries)

        return answer
    
def _load_dataset(path):
    with open(path + "/embeddings.json", 'r', encoding='utf-8') as file:
        embeddings = json.load(file)["embeddings"]
    with open(path + "/entities.json", 'r', encoding='utf-8') as file:
        entities = json.load(file)["entities"]
    with open(path + "/summaries.json", 'r', encoding='utf-8') as file:
        summaries = json.load(file)
    return summaries, embeddings, entities

def new_server(path) -> QueryServer:
    summaries, embeddings, entities = _load_dataset(path)
    return QueryServer(summaries=summaries, embeddings=embeddings, entities=entities, client=OpenAI())

# Test main, which accepts queries from stdin.
if __name__ == '__main__':
    summaries, embeddings, entities = _load_dataset(sys.argv[1])
    server = QueryServer(summaries=summaries, embeddings=embeddings, entities=entities, client=OpenAI())
    try:
        while True:
            user_input = input("> ")
            if user_input == "quit":
                break
            print(server.handle_query(user_input))
    except KeyboardInterrupt:
        print("\nExiting...")