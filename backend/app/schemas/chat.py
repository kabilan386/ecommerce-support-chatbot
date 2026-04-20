from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator

from app.models.message import MessageRole


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class MessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    sentiment_score: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    messages: list[MessageResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def ensure_messages_list(cls, data: Any) -> Any:
        if hasattr(data, "messages"):
            msgs = data.messages
            if msgs is None:
                data.__dict__["messages"] = []
            elif not isinstance(msgs, list):
                data.__dict__["messages"] = [msgs]
        return data
