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

### Task 3: Intent-Based Natural Language Routing (Completed)

Added LLM-powered intent routing so users can ask questions in plain text. The LLM decides which tool (API call) to invoke based on the user's query.

**Implementation:**
- Created `services/llm_client.py` with `LLMClient` and `IntentRouter` classes
- Defined 9 tool schemas for all backend endpoints
- Implemented tool calling loop: user message → LLM → tool execution → results back to LLM → final answer
- Added inline keyboard buttons for common queries in `handlers/natural_language.py`
- Updated `bot.py` to handle plain text messages and callback queries

**Key patterns:**
- **Tool descriptions > prompt engineering** — Clear tool descriptions help the LLM choose correctly
- **No regex routing** — The LLM decides which tool to call based on tool descriptions
- **Tool calling loop** — Results are fed back to the LLM for multi-step reasoning
- **Separation of concerns** — LLM client handles chat, API client handles backend, router orchestrates

**Tool schemas defined:**
1. `get_items` — List all labs and tasks
2. `get_learners` — List enrolled students and groups
3. `get_scores` — Score distribution for a lab
4. `get_pass_rates` — Per-task pass rates for a lab
5. `get_timeline` — Submission timeline for a lab
6. `get_groups` — Per-group scores and student counts
7. `get_top_learners` — Top N learners by score
8. `get_completion_rate` — Completion rate percentage
9. `trigger_sync` — Refresh data from autochecker

**Inline keyboard buttons:**
- 8 action buttons (labs, scores, top students, groups, pass rates, completion, learners, sync)
- 3 quick query buttons (what labs, lowest pass rate, best group)

**Files modified/created:**
- `services/llm_client.py` — LLM client and intent router (new)
- `services/api_client.py` — Added 9 new API methods for tools
- `handlers/natural_language.py` — Natural language handler and keyboard buttons (new)
- `handlers/__init__.py` — Exported new handlers
- `bot.py` — Added plain text message handling and inline keyboard support

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
│   ├── commands.py         # Command handlers (/start, /help, etc.)
│   └── natural_language.py # LLM intent router and inline keyboards
└── services/
    ├── __init__.py
    ├── api_client.py       # LMS API client
    └── llm_client.py       # LLM client with tool calling
```

## Next Steps

1. ✅ Task 1: Verify acceptance criteria
2. ✅ Task 2: Backend integration complete
3. ✅ Task 3: LLM intent routing complete
4. ⏳ Task 4: Containerize and deploy

## Git Workflow

For each task:
1. Create issue on GitHub
2. Create branch: `task-N-short-description`
3. Implement and test
4. Create PR with `Closes #N` in description
5. Partner review
6. Merge to main
