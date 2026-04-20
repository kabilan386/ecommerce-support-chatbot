from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus

ESCALATION_THRESHOLD = -0.3
ESCALATION_CONSECUTIVE = 3


async def should_escalate(recent_messages: list[Message]) -> bool:
    """Return True if last 3 user messages all have sentiment below threshold."""
    user_msgs = [m for m in recent_messages if m.role.value == "user" and m.sentiment_score is not None]
    if len(user_msgs) < ESCALATION_CONSECUTIVE:
        return False
    return all(m.sentiment_score < ESCALATION_THRESHOLD for m in user_msgs[-ESCALATION_CONSECUTIVE:])


async def create_ticket(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    title: str,
    description: str,
    category: TicketCategory = TicketCategory.general,
    escalate: bool = False,
) -> Ticket:
    priority = TicketPriority.high if escalate else TicketPriority.medium
    ticket = Ticket(
        conversation_id=conversation_id,
        user_id=user_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        status=TicketStatus.open,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


def detect_category(text: str) -> TicketCategory:
    text_lower = text.lower()
    if any(w in text_lower for w in ["return", "exchange"]):
        return TicketCategory.return_
    if any(w in text_lower for w in ["refund", "money back"]):
        return TicketCategory.refund
    if any(w in text_lower for w in ["ship", "deliver", "tracking"]):
        return TicketCategory.shipping
    if any(w in text_lower for w in ["pay", "charge", "invoice", "billing"]):
        return TicketCategory.payment
    if any(w in text_lower for w in ["order", "purchase"]):
        return TicketCategory.order
    return TicketCategory.general
