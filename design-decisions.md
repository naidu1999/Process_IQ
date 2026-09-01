# Design Decisions

The weighted deterministic score is intentionally explainable. New process data is read at runtime and persisted through the API. The current Q&A endpoint is retrieval-style and modular, so an LLM/RAG service can later replace it behind the same API contract.
