import asyncio

import google.generativeai as genai

from app.config import settings

genai.configure(api_key=settings.gemini_api_key)

SYSTEM_PROMPT = """You are a helpful e-commerce customer support assistant.
You assist customers with orders, returns, refunds, shipping, and payment queries.
Be concise, empathetic, and solution-focused.

IMPORTANT RULES:
- NEVER ask the customer for more details before helping. Work with what they give you.
- If a customer mentions a payment issue, refund, return, missing order, or shipping problem — immediately acknowledge it and create a ticket right away.
- Do NOT ask for order numbers, payment methods, or error messages before creating a ticket.
- After acknowledging the issue, tell the customer: "I've raised a support ticket for you and our team will follow up shortly."
- Only add [UNRESOLVED] at the end if you cannot fully resolve the issue yourself (e.g. refund processing, order investigation).
- For simple questions you CAN answer (e.g. return policy, delivery timeframes), answer directly without [UNRESOLVED].

Example:
Customer: "I have a payment issue"
You: "I'm sorry to hear you're facing a payment issue. I've raised a support ticket for you and our team will look into it and follow up shortly. [UNRESOLVED]"
"""


def _build_gemini_history(messages: list[dict]) -> list[dict]:
    """Convert OpenAI-style messages to Gemini chat history format."""
    history = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    return history


async def stream_response(messages: list[dict]):
    """Yield text chunks from Gemini for the given conversation messages."""
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    history = _build_gemini_history(messages)
    # Last message is the current user query
    last_message = history[-1]["parts"][0] if history else ""
    chat_history = history[:-1] if len(history) > 1 else []

    chat = model.start_chat(history=chat_history)

    def sync_stream():
        return chat.send_message(last_message, stream=True)

    stream = await asyncio.to_thread(sync_stream)

    for chunk in stream:
        if chunk.text:
            yield chunk.text


def build_context(db_messages: list) -> list[dict]:
    """Return last 10 messages formatted for Gemini."""
    recent = db_messages[-10:]
    return [{"role": msg.role.value, "content": msg.content} for msg in recent]


def is_unresolved(response_text: str) -> bool:
    return "[UNRESOLVED]" in response_text
