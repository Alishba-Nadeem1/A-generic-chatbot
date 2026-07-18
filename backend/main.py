
import os
import re
import json
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "business_data.json"
FRONTEND_DIR = BASE_DIR / "frontend"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    business = json.load(f)

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY") or "not-set",
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "llama-3.3-70b-versatile"

app = FastAPI(title="Hybrid Support Desk Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# session_id -> list of {"role": "user"/"assistant", "content": str}
conversation_history = {}

ORDER_ID_PATTERN = re.compile(r"\bORD\d{3,6}\b", re.IGNORECASE)


def build_system_prompt():
    products_text = "\n".join(
        f"- {p['name']} ({p['id']}): {p['price']}, {p['stock']}"
        for p in business["products"]
    )
    return f"""You are a helpful, friendly customer support agent for {business['company_name']}.

ABOUT THE BUSINESS:
{business['about']}

BUSINESS HOURS:
{business['business_hours']}

POLICIES:
- Refunds: {business['policies']['refund_policy']}
- Cancellations: {business['policies']['cancellation_policy']}
- Shipping: {business['policies']['shipping_policy']}

PRODUCT CATALOG:
{products_text}

RULES:
- Only answer using the business information given above. Don't invent policies or products that aren't listed.
- If the user provides an order ID and order lookup data is given to you in the conversation, use that exact data to answer — don't make up order details yourself.
- If a user wants to cancel, get a refund, or file a complaint, be empathetic, explain the relevant policy, and ask for their order ID if you don't have it yet.
- If the user asks something totally unrelated to this business, politely redirect them back to what you can help with.
- Keep replies concise and conversational, like a real support agent — not overly long.
"""


def lookup_order_if_mentioned(message: str) -> str | None:
    """Rule-based layer: detect an order ID in the message and look it up
    in the mock database. Returns a note to inject into context, or None."""
    match = ORDER_ID_PATTERN.search(message)
    if not match:
        return None

    order_id = match.group(0).upper()
    order = business["mock_orders"].get(order_id)

    if order:
        return (
            f"[SYSTEM NOTE: Order {order_id} found in database — "
            f"status: {order['status']}, items: {order['items']}, eta: {order['eta']}. "
            f"Use this exact information to answer the user.]"
        )
    return f"[SYSTEM NOTE: Order {order_id} was not found in the database. Let the user know it wasn't found and ask them to double check the order ID.]"


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    used_order_lookup: bool
    timestamp: str


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = conversation_history.setdefault(req.session_id, [])

    user_content = req.message
    order_note = lookup_order_if_mentioned(req.message)
    if order_note:
        user_content = f"{req.message}\n\n{order_note}"

    history.append({"role": "user", "content": user_content})

    messages_for_api = [{"role": "system", "content": build_system_prompt()}] + history

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=400,
        messages=messages_for_api,
    )

    reply_text = response.choices[0].message.content

    
    history.append({"role": "assistant", "content": reply_text})

    return ChatResponse(
        reply=reply_text,
        used_order_lookup=bool(order_note),
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )


@app.get("/history/{session_id}")
def get_history(session_id: str):
    return conversation_history.get(session_id, [])


@app.get("/health")
def health_check():
    key_set = bool(os.environ.get("GROQ_API_KEY"))
    return {"status": "ok", "api_key_configured": key_set}
