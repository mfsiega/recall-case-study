import json
import logging
import sys
from openai import OpenAI
from backend.src import build_entity_graph
from backend.src.answer_generator import AnswerGenerator
from backend.src.related_summary_finder import RelatedSummaryFinder
from backend.src.related_topic_generator import topic_generator_for_entity_graph

LOG = logging.getLogger('uvicorn.error')

class QueryServer:
    def __init__(self, summaries, embeddings, entities, client: OpenAI):
        self.related_summary_finder = RelatedSummaryFinder(client, embeddings)
        self.answer_generator = AnswerGenerator(client, summaries)
        self.entity_graph = build_entity_graph.build_graph(entities)
        self.related_topic_generator = topic_generator_for_entity_graph(
            self.entity_graph
        )
        self.entities = entities

    def _get_related_topic_info(self, related_topics):
        results = []
        for topic in related_topics:
            # Find the summary nodes that are connected to this topic.
            references = ", ".join(str(node)
                          for node in self.entity_graph.neighbors(topic) 
                          if self.entity_graph.nodes[node]['type'] == 'SUMMARY')
            results.append(f"""
            {topic}: mentioned in summary {references}
            """)
        return "\n".join(results)

    def handle_query(self, query):
        related_summaries = self.related_summary_finder.find(query)
        LOG.info("Related summaries: %s", related_summaries)
        answer = self.answer_generator.generate(query, related_summaries)
        related_topics = self.related_topic_generator.generate(query)
        related_topic_info = self._get_related_topic_info(related_topics)
        return "\n\n".join([answer, related_topic_info])
    
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