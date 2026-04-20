from datetime import datetime

from pydantic import BaseModel

from app.models.ticket import TicketCategory, TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str
    description: str | None = None
    category: TicketCategory = TicketCategory.general
    conversation_id: int


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    category: TicketCategory | None = None


class TicketResponse(BaseModel):
    id: int
    conversation_id: int
    user_id: int
    title: str
    description: str | None
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
