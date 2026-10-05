# AI-Powered Healthcare Intelligence & Patient Support Platform

Portfolio / educational project. **Not a medical diagnosis system.** It uses
synthetic data only and is designed to avoid diagnosis or personal treatment advice.

## Problem
Answer healthcare questions from trusted documents (RAG), analyze synthetic
patient data (SQL + Pandas), and route each question to the right capability
with a LangGraph supervisor, with safety checks before and after.

## Architecture (target)
User -> FastAPI -> Safety/Guardrail -> LangGraph Supervisor -> RAG Agent | Analytics Agent
-> FAISS | SQLite -> LLM (AWS Bedrock) -> Response validation -> Answer

## Status
- [x] Phase 1: foundation
- [ ] Phase 2: RAG
- [ ] Phase 3: healthcare data + analytics agent
- [ ] Phase 4: agents + LangGraph supervisor
- [ ] Phase 5: safety + evaluation
- [ ] Phase 6: API, logging, Docker, UI

## Setup
    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env             # fill in values; never commit .env
    python tests/test_foundation.py

## Technologies
Python, LangChain, LangGraph, AWS Bedrock, FAISS, SQLite, Pandas, FastAPI, Streamlit, Docker, RAGAS
