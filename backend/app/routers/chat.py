import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.user import User
from app.schemas.chat import ChatRequest, ConversationResponse
from app.services import chat_service, sentiment_service, ticket_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = Conversation(user_id=current_user.id)
    db.add(conv)
    await db.commit()
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conv.id)
    )
    return result.scalar_one()


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/message")
async def send_message(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Resolve or create conversation
    if body.conversation_id:
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.id == body.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(user_id=current_user.id)
        db.add(conv)
        await db.commit()
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conv.id)
        )
        conv = result.scalar_one()

    # Save user message with sentiment
    sentiment = sentiment_service.score(body.message)
    user_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.user,
        content=body.message,
        sentiment_score=sentiment,
    )
    db.add(user_msg)
    await db.commit()

    # Fetch last 10 messages for context
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    all_msgs = result.scalars().all()
    context = chat_service.build_context(all_msgs)

    async def event_stream():
        full_response = ""
        yield f"data: {json.dumps({'conversation_id': conv.id})}\n\n"

        async for chunk in chat_service.stream_response(context):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.assistant,
            content=full_response,
            sentiment_score=None,
        )
        db.add(assistant_msg)

        # Auto-create ticket if unresolved
        if chat_service.is_unresolved(full_response):
            escalate = await ticket_service.should_escalate(all_msgs)
            category = ticket_service.detect_category(body.message)
            await ticket_service.create_ticket(
                db=db,
                conversation_id=conv.id,
                user_id=current_user.id,
                title=f"Support request: {body.message[:80]}",
                description=body.message,
                category=category,
                escalate=escalate,
            )

        await db.commit()
        yield f"data: {json.dumps({'done': True, 'unresolved': chat_service.is_unresolved(full_response)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
