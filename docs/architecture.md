# Architecture

- **FastAPI backend** with modular layers for routes, agent orchestration, safety checks, and schemas.
- **React frontend** for chat + symptom intake and structured rendering.
- **Safety guardrails** implemented as editable keyword rule sets and output checks.
- **LLM abstraction** supports OpenAI-compatible APIs and deterministic fallback mode.
- **Session memory** currently in-memory with easy adapter replacement for Redis/DB.
