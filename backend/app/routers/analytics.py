from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.message import Message
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.schemas.analytics import KPIResponse, TrendPoint, TrendsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/kpi", response_model=KPIResponse)
async def get_kpi(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    total = await db.scalar(select(func.count(Ticket.id)))
    open_count = await db.scalar(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.open))
    resolved = await db.scalar(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.resolved)
    )
    avg_sentiment = await db.scalar(
        select(func.avg(Message.sentiment_score)).where(Message.sentiment_score.isnot(None))
    )

    resolution_rate = (resolved / total * 100) if total else 0.0
    return KPIResponse(
        total_tickets=total or 0,
        open_tickets=open_count or 0,
        resolved_tickets=resolved or 0,
        avg_sentiment=round(avg_sentiment or 0.0, 3),
        resolution_rate=round(resolution_rate, 1),
    )


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    since = datetime.now(timezone.utc) - timedelta(days=30)

    rows = await db.execute(
        select(
            func.date(Ticket.created_at).label("date"),
            func.count(Ticket.id).label("count"),
        )
        .where(Ticket.created_at >= since)
        .group_by(func.date(Ticket.created_at))
        .order_by(func.date(Ticket.created_at))
    )
    daily = [TrendPoint(date=str(r.date), count=r.count) for r in rows]

    sentiment_rows = await db.execute(
        select(
            func.date(Message.created_at).label("date"),
            func.avg(Message.sentiment_score).label("avg_score"),
        )
        .where(Message.created_at >= since, Message.sentiment_score.isnot(None))
        .group_by(func.date(Message.created_at))
        .order_by(func.date(Message.created_at))
    )
    sentiment_trend = [
        {"date": str(r.date), "avg_score": round(r.avg_score, 3)} for r in sentiment_rows
    ]

    return TrendsResponse(daily_tickets=daily, sentiment_trend=sentiment_trend)
