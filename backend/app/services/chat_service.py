from openai import AsyncOpenAI

from app.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

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


async def stream_response(messages: list[dict]):
    """Yield text chunks from GPT-4o for the given conversation messages."""
    stream = await _client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        stream=True,
        temperature=0.7,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def build_context(db_messages: list) -> list[dict]:
    """Return last 10 messages formatted for OpenAI API."""
    recent = db_messages[-10:]
    return [{"role": msg.role.value, "content": msg.content} for msg in recent]


def is_unresolved(response_text: str) -> bool:
    return "[UNRESOLVED]" in response_text
