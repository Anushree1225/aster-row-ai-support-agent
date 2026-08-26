from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agent.agent import answer_user


app = FastAPI(
    title="Aster & Row AI Support Agent",
    description="RAG-powered customer support API",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Aster & Row AI Support Agent",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        answer = answer_user(message)

        return ChatResponse(
            answer=answer,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the request.",
        ) from exc