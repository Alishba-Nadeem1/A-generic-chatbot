# Support Desk — Hybrid AI Customer Support Chatbot

A customer support chatbot that understands natural language like ChatGPT, while staying strictly grounded in real business data — no hallucinated policies, no invented order details.

## Overview

Traditional rule-based chatbots break the moment a user phrases something unexpectedly. Pure LLM chatbots, on the other hand, can confidently make things up. This project combines both approaches:

- **LLM layer** (Groq API, Llama 3.3 70B) handles natural language understanding — typos, rephrasing, follow-up questions, casual tone — the way a real support agent would.
- **Rules layer** grounds every response in actual business data: company policies, product catalog, and a live order-lookup system, so the model can't invent information it wasn't given.

## Features

- Natural conversation handling (typos, rephrasing, multi-turn context)
- Order lookup via regex-based ID detection, cross-referenced against a mock order database
- Responses strictly grounded in real business policies and product data — no hallucination
- Session-based conversation memory
- REST API built with FastAPI (`/chat`, `/history/{session_id}`, `/health`)
- Custom-designed chat UI with a light hero landing page and dark live-chat window

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq API (Llama 3.3 70B), via OpenAI-compatible SDK |
| Backend | FastAPI, Python |
| Frontend | HTML/CSS/JS |
| Data | JSON-based business rules & mock order database |

## Architecture
