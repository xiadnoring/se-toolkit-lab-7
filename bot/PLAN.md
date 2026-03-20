# LMS Telegram Bot — Development Plan

This document outlines the approach for building a Telegram bot that integrates with the LMS backend.

## Overview

We are building a Telegram bot that allows students to interact with the LMS backend through chat. The bot supports slash commands for common actions and uses an LLM to interpret natural language queries.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point (`bot.py`)** — Handles CLI arguments (`--test` mode) and Telegram integration using aiogram
2. **Handlers (`handlers/`)** — Pure functions that process commands and return text responses
3. **Services (`services/`)** — External API clients (LMS backend API client with Bearer auth)
4. **Configuration (`config.py`)** — Environment variable loading from `.env.bot.secret`

This architecture enables **testable handlers**: the same handler functions work in `--test` mode, unit tests, and Telegram without modification. This is called **separation of concerns** — the business logic (handlers) is independent of the transport layer (Telegram).

## Task Breakdown

### Task 1: Plan and Scaffold (Completed)

Created the project skeleton with `--test` mode. Handlers return responses and the test mode calls them directly without Telegram.

**Deliverables:**
- `bot/bot.py` with `--test` mode and Telegram integration
- `bot/handlers/` directory with command handlers
- `bot/pyproject.toml` for dependencies (aiogram, httpx, python-dotenv)
- `bot/PLAN.md` (this file)
- `bot/config.py` for environment loading
- `bot/services/` for API clients

### Task 2: Backend Integration (Completed)

Connected handlers to the LMS backend API. Added real data fetching to `/health`, `/labs`, and `/scores` commands. Implemented an API client service with Bearer token authentication.

**Key patterns:**
- API client reads `LMS_API_URL` and `LMS_API_KEY` from environment
- Uses `httpx.AsyncClient` for async HTTP requests
- Graceful error handling when backend is unreachable or returns errors
- Proxy environment variables are cleared at module load to avoid httpx conflicts

**Endpoints used:**
- `GET /items/` — Health check and lab listing
- `GET /analytics/scores` — Score data (for future enhancement)

### Task 3: Intent-Based Natural Language Routing (Planned)

Add LLM-powered intent routing so users can ask questions in plain text. The LLM decides which tool (API call) to invoke based on the user's query.

**Approach:**
- Define tool descriptions for each backend endpoint
- Use the LLM to parse user intent and select tools
- Chain multiple API calls when needed (e.g., "show my lab-04 scores and compare to group average")
- Tool descriptions are more important than prompt engineering — clear descriptions help the LLM choose correctly

**Key pattern:** The LLM reads tool descriptions to decide which to call. If the LLM picks the wrong tool, improve the description — don't route around it with regex.

### Task 4: Containerize and Document (Planned)

Package the bot in Docker and deploy alongside the backend. Update documentation with deployment instructions.

**Deliverables:**
- `bot/Dockerfile` — Multi-stage build for small image
- Update `docker-compose.yml` with bot service
- README with deployment guide
- Docker networking: containers use service names, not `localhost`

## Testing Strategy

1. **Test mode** — `--test "/command"` for quick manual verification without Telegram
2. **Unit tests** — Test handlers in isolation (future enhancement)
3. **Integration tests** — Test with real backend (future enhancement)
4. **Telegram testing** — Manual testing in Telegram after deployment

## Environment Files

- `.env.bot.secret` — Bot token, LMS API credentials, LLM credentials (gitignored)
- `.env.bot.example` — Template with placeholder values
- `.env.docker.secret` — Backend credentials for Docker Compose

## Files Structure

```
bot/
├── bot.py              # Entry point (--test mode + Telegram)
├── config.py           # Environment loading
├── pyproject.toml      # Dependencies
├── PLAN.md             # This file
├── .env.bot.secret     # Configuration (gitignored)
├── handlers/
│   ├── __init__.py
│   └── commands.py     # Command handlers
└── services/
    ├── __init__.py
    └── api_client.py   # LMS API client
```

## Next Steps

1. ✅ Task 1: Verify acceptance criteria
2. ✅ Task 2: Backend integration complete
3. ⏳ Task 3: Implement LLM intent routing
4. ⏳ Task 4: Containerize and deploy

## Git Workflow

For each task:
1. Create issue on GitHub
2. Create branch: `task-N-short-description`
3. Implement and test
4. Create PR with `Closes #N` in description
5. Partner review
6. Merge to main
