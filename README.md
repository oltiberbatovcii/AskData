# AskData

Chat with a database in plain language. Ask a question like *"Top 5 customers by total spending"*, and AskData finds the relevant tables (RAG), has an LLM write SQL, validates it for safety, runs it on a **read-only** SQLite database, and explains the result.

Built on the [Chinook](https://github.com/lerocha/chinook-database) sample database (a digital music store).

> 🚧 Work in progress — a hands-on learning project. Setup instructions, architecture and results will be added as the project grows.

## Planned stack

- **Backend:** Python, FastAPI, SQLite, sqlglot, ChromaDB, sentence-transformers, Ollama
- **Frontend:** React + TypeScript (Vite)
- **Tooling:** pytest, ruff, Docker Compose
