from typing import Literal

from pydantic import BaseModel, Field


class IncomingMessage(BaseModel):
    id: str | None = None
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[IncomingMessage]
    language: Literal["en", "rw"] = "en"


class Classification(BaseModel):
    intent: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE", "DISTRESSED"]
    needs_research: bool
    explanation: str


class ChatResponse(BaseModel):
    classification: Classification
    final_response: str
    sources: list[str] = Field(default_factory=list)


class SaveMessageRequest(BaseModel):
    chat_id: str = Field(alias="chatId")
    role: Literal["user", "assistant"]
    content: str
    risk_level: str | None = Field(default=None, alias="riskLevel")
    language: Literal["en", "rw"] = "en"


class ChatOut(BaseModel):
    id: str
    user_id: str
    title: str | None
    created_at: str


class MessageOut(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    risk_level: str | None
    language: str | None
    created_at: str
