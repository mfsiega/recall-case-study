from openai import OpenAI


class AnswerGenerator:
    def __init__(self, client: OpenAI, summaries):
        self.client = client
        self.summaries = []
        # I'm not sure why I made the summaries JSON shaped like this, but
        # now we have to do some wrangling.
        for i in range(len(summaries)):
            self.summaries.append(summaries[str(i)])

    def _construct_query_prompt(self, query, relevant_summary_indices):
        context = "\n\n".join([f"Summary {i}: {self.summaries[i]}" for i in relevant_summary_indices])
        return f"""
                The user has asked a question. Answer the question, based on the information in the listed summaries provided.

                Summaries:
                {context}

                User question: {query}

                Answer:
                """

    def generate(self, query, relevant_summary_indices):
        query_prompt = self._construct_query_prompt(query, relevant_summary_indices)
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": query_prompt}
            ]
        ).choices[0].message.content