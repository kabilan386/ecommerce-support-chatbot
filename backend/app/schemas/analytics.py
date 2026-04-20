from pydantic import BaseModel


class KPIResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    avg_sentiment: float
    resolution_rate: float


class TrendPoint(BaseModel):
    date: str
    count: int


class TrendsResponse(BaseModel):
    daily_tickets: list[TrendPoint]
    sentiment_trend: list[dict]
