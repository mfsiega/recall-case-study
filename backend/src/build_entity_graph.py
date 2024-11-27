import json
import sys
import networkx as nx
import matplotlib.pyplot as plt

# Our graph has three types of nodes:
#
# - Entities
# - Topics/concepts
# - Summaries (our documents)
# 
# There are edges between each entity and its related topics.
# There are also edges between each summary and all of its entities and topics.
def build_graph(entities) -> nx.Graph:
    G = nx.Graph()
    summaryIndex = 0
    for summary_entities in entities:
        extracted = summary_entities[str(summaryIndex)] # the data is structured a bit oddly
        for e in extracted:
            entity_name = e["name"]
            related_topics = e["related_topics"]
            G.add_node(summaryIndex, type="SUMMARY")
            G.add_node(entity_name, type="ENTITY")
            G.add_edge(summaryIndex, entity_name)
            for topic in related_topics:
                G.add_node(topic, type="TOPIC")
                G.add_edge(entity_name, topic)
                G.add_edge(summaryIndex, topic)
        summaryIndex += 1
    return G

def build_graph_from_entities_file(path) -> nx.Graph:
    with open(path, 'r', encoding='utf-8') as file:
        entities = json.load(file)["entities"]
    return build_graph(entities)

if __name__ == '__main__':
    path = sys.argv[1]
    G = build_graph_from_entities_file(path)
    nx.draw(G, with_labels=True)
    plt.show()