# Support Desk — Hybrid LLM + Business-Rules Customer Support Chatbot

A customer support chatbot that combines **real language understanding** (via the Groq API (free, Llama 3.3 70B)) with **hard-coded business rules and data**, so it actually understands rephrasing/typos/follow-ups like ChatGPT, while staying grounded in this business's real policies, products, and orders instead of hallucinating.

An earlier version of this project (`backend/main_intent_classifier_backup.py`) used a TF-IDF + Logistic Regression intent classifier — kept in the repo to show the evolution from a classic ML approach to an LLM-based one.

## How the hybrid works
1. **LLM layer (understanding):** Every message goes to Claude, which reads a system prompt containing the business's real info — hours, refund/cancellation/shipping policy, and product catalog — so it answers accurately and can't invent details.
2. **Rules layer (grounding):** If a message contains an order ID (e.g. `ORD1001`), the backend looks it up in a mock order database (`data/business_data.json`) *before* calling Claude, and hands Claude the real result. Claude explains it in natural language, but the actual data comes from your system, not the model's imagination.
3. **Memory:** Full conversation history is kept per session, so follow-up questions ("and how long will that take?") work naturally.

## Features
- Handles typos, rephrasing, and casual language naturally (no training data needed)
- Grounded in real business data — won't invent policies or product details
- Rule-based order lookup layer (swap the mock DB for a real one in production)
- Session-based multi-turn conversation memory
- REST API (`/chat`, `/history/{session_id}`, `/health`)
- Same helpdesk-styled chat UI as before

## Tech Stack
- **LLM**: Groq API (free, Llama 3.3 70B) (`llama-3.3-70b-versatile`) via the `openai` Python SDK
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Vanilla HTML/CSS/JS chat widget

## Project Structure
```
chatbot-project/
├── data/
│   ├── business_data.json          # company info, policies, products, mock orders
│   └── intents.json                # (legacy, used by the old classifier version)
├── model/
│   ├── train.py                    # (legacy) trains the old intent classifier
│   └── chatbot_model.pkl           # (legacy) trained classifier
├── backend/
│   ├── main.py                      # current hybrid LLM+rules FastAPI app
│   └── main_intent_classifier_backup.py  # old intent-classifier version, kept for reference
├── frontend/
│   └── index.html                   # chat UI
├── .env.example                     # template for your API key
└── README.md
```

## How to Run

1. **Install dependencies:**
   ```
   pip install fastapi uvicorn pydantic openai python-dotenv  # openai SDK works with Groq too
   ```

2. **Add your API key:**
   - Rename `.env.example` to `.env`
   - Open it and replace `your-api-key-here` with your real Groq API key from [console.groq.com/keys](https://console.groq.com/keys) (free, no credit card needed)

3. **Start the server:**
   ```
   python -m uvicorn backend.main:app --reload --port 8000
   ```

4. Open `http://localhost:8000` in your browser.

## Try it out
- "where is my order ORD1001" → looks up the real mock order and answers with actual status
- "what's your refund policy" → answers from the real policy text
- "can you tell me more about your business" → answers naturally even with typos or rephrasing
- Follow-up questions work too, e.g. after asking about refunds: "how long does that take?"

## API Example

**POST** `/chat`
```json
{ "message": "where is my order ORD1001", "session_id": "abc123" }
```

**Response**
```json
{
  "reply": "I found your order! ORD1001 (Wireless Bluetooth Earbuds) has shipped and should arrive in about 2 days.",
  "used_order_lookup": true,
  "timestamp": "2026-07-17T10:15:00"
}
```

## Next Steps / Possible Extensions
- Replace the mock order database with a real one (SQL/NoSQL)
- Add more rule-based lookups (e.g. detecting product names and pulling live stock data)
- Add streaming responses for a more natural typing effect in the UI
- Deploy backend on Render/Railway and frontend on Vercel for a live demo link
- For the portfolio/interview story: mention both versions — shows you understand classic ML (TF-IDF classifier) *and* when/why an LLM-based approach is the better tool
