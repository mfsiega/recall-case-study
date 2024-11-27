# Recall AI Case Study

Michael Siega, mf.siega@gmail.com, 2024-11-26

## Prompt

Create a chat application that allows users to interact with a dataset of video summaries.

## Approach

There are three main components to the codebase:

- Frontend, to present the chat interface.
- Backend, to handle chat queries about the dataset.
- Preprocessing, to generate initial context to serve requests.

A quick overview of these components below.

### Preprocessing

To efficiently serve queries based on the dataset, we take some preprocessing steps:

1. Generate embeddings for the summaries. This will support semantic search for incoming queries.
2. Entity extraction for the summaries. This will allow us to efficiently find related entities and summaries for the queries.
3. Store and index the generated metadata to map between the summaries and their data.

TODO: figure out what data stores I need. Probably I should use a graph db, but I might just do an in-memory graph.

### Frontend

A simple single-page React app. There are a lot of possible future improvements here:

- Nicer UX/visuals
- Query history

TODO: pick a component that implements the chat window.

### Backend

The API is implemented in Python with FastAPI. This was chosen because the query handling interacts with some machine learning APIs, and these are most convenient to use in Python.

At a high level, query handling involves:

- Generate an embedding for the query.
- Use cosine similarity to find the top N most related summaries.
- Construct a prompt like: `Answer the question ${query} based on the following summaries: [summary1, summary2, ... summaryN]`, send this to the Chat Completion API.
- Extract entities using spaCy.

## Notes

### An alternative approach

The approach I'm starting with is:

- Using the embeddings of the summaries and the query to identify which summaries are closest to the query itself.
- Then pose the query to the LLM, giving the 3 closest summaries as context.
- Extract the entities from the answer.
- For each top extracted entity, list the summaries that include that entity.

An alternative:

- Pose the query directly to the LLM with no context.
- Extract the entities from the answer.
- Again, list the summaries that include the extracted entities.

The case I'm thinking about here: if I pose a question to the system that has no connection to my documents, it should recognize that and reject the question, instead of giving a bad answer. I also might want to optimize for a "generally" correct answer rather than the one based on what happens to be in my documents.

This doesn't work at all if my documents aren't already in the LLM. It's not clear that one approach is strictly better than another.
