from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ticket import Ticket
from app.models.user import User, UserRole
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services.ticket_service import create_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.admin or current_user.role == UserRole.agent:
        result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    else:
        result = await db.execute(
            select(Ticket).where(Ticket.user_id == current_user.id).order_by(Ticket.created_at.desc())
        )
    return result.scalars().all()


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket_endpoint(
    body: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_ticket(
        db=db,
        conversation_id=body.conversation_id,
        user_id=current_user.id,
        title=body.title,
        description=body.description or "",
        category=body.category,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role == UserRole.customer and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    body: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if body.status:
        ticket.status = body.status
    if body.priority:
        ticket.priority = body.priority
    if body.category:
        ticket.category = body.category

    await db.commit()
    await db.refresh(ticket)
    return ticket
