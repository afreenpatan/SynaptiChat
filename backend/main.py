from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from summarizer import summarize_text


app = FastAPI(
    title="SmartChat API",
    description="AI-powered Chat Log Summarization System",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {
        "message": "Welcome to SmartChat API",
        "status": "running"
    }


@app.post("/summarize")
def summarize(request: ChatRequest):
    summary = summarize_text(request.text)

    return {
        "summary": summary
    }