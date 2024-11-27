import faiss
import numpy as np
from openai import OpenAI

# Given some query, it finds summaries that are most closely related.
# It does this with FAISS (Facebook AI Similarity Search) over the embeddings
# of the set of summaries for the given query.
class RelatedSummaryFinder:
    def __init__(self, client: OpenAI, embeddings):
        self.client = client
        self.embeddings = np.array(embeddings)
        self.faiss_index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.faiss_index.add(self.embeddings)

    def _embeddings_for_query(self, query):
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        return response.data[0].embedding
    
    def _relevant_summary_indices(self, query_embedding, N=5):
        _, indices = self.faiss_index.search(np.array([query_embedding]), N)
        return indices[0]

    def find(self, query):
        query_embedding = self._embeddings_for_query(query)
        return self._relevant_summary_indices(query_embedding)