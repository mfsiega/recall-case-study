from fastapi import FastAPI
from backend.src.server import new_server
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
server = new_server("/home/mfsiega/recall-case-study/backend/data")

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