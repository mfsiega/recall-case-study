from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from backend.src.server import new_server

app = FastAPI()
server = new_server(os.environ["DATA_DIR"] or "/backend/data")

# Define allowed origins (add your Next.js app URL here)
origins = [
    "http://localhost:3000",  # Next.js development server
    "http://127.0.0.1:3000",  # Alias for localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from these origins
    allow_credentials=True,  # Allow cookies or authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Query(BaseModel):
    role: str
    content: str

@app.post("/")
async def root(query: Query):
    answer = server.handle_query(query.content)
    return {"reply": answer}

@app.get("/summaries/{summary_id}")
async def get_summary(summary_id: str):
    return {"summary": server.summaries[summary_id]}