from openai import OpenAI


class AnswerGenerator:
    def __init__(self, client: OpenAI, summaries):
        self.client = client
        self.summaries = summaries

    def _construct_query_prompt(self, query, relevant_summary_indices):
        relevant_summaries = [self.summaries[index] for index in relevant_summary_indices]
        context = "\n\n".join([f"{i+1}. {summary}" for i, summary in enumerate(relevant_summaries)])
        return f"""
                The user has asked a question. Answer the question, based on the information in the listed summaries provided.

                Summaries:
                {context}

                User question: {query}

                Answer:
                """

    def generate_answer(self, query, relevant_summary_indices):
        query_prompt = self._construct_query_prompt(query, relevant_summary_indices)
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": query_prompt}
            ]
        ).choices[0].message.content