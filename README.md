# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

This section documents how to deploy the Telegram bot alongside the LMS backend using Docker Compose.

### Prerequisites

- Docker and Docker Compose installed on the VM
- Backend already running (from previous tasks)
- Telegram bot token from @BotFather
- LLM API credentials (Qwen Code API)

### Environment variables

Create `.env.docker.secret` in the project root with the following variables:

```bash
# Telegram bot token (from @BotFather)
BOT_TOKEN=your-telegram-bot-token-here

# LMS API
LMS_API_KEY=my-secret-api-key

# LLM API
LLM_API_KEY=your-qwen-api-key
LLM_API_BASE_URL=http://10.91.49.208:42005/v1
LLM_API_MODEL=coder-model
```

The bot service in `docker-compose.yml` uses these environment variables:
- `BOT_TOKEN` — Telegram bot authentication
- `LMS_API_URL` — Internal network URL to backend (`http://backend:8000`)
- `LMS_API_KEY` — Backend API authentication
- `LLM_API_KEY`, `LLM_API_BASE_URL`, `LLM_API_MODEL` — LLM configuration

### Build and deploy

1. **Pull latest code** (if deploying from GitHub):
   ```bash
   cd ~/se-toolkit-lab-7
   git pull
   ```

2. **Build and start the bot**:
   ```bash
   cd ~/se-toolkit-lab-7
   docker compose --env-file .env.docker.secret up --build -d bot
   ```

3. **Verify the bot is running**:
   ```bash
   docker compose ps bot
   docker compose logs bot
   ```

   You should see:
   ```
   NAME                STATUS
   se-toolkit-lab-7-bot-1   Up (healthy)
   ```

4. **Verify backend is still healthy**:
   ```bash
   curl -sf http://localhost:42002/items/ -H "Authorization: Bearer my-secret-api-key" | head -c 100
   ```

### Test in Telegram

1. Open your bot in Telegram
2. Send `/start` — should receive welcome message with inline keyboard
3. Send `/help` — should see available commands with quick query buttons
4. Send `/health` — should see backend status
5. Send `/labs` — should list available labs
6. Send plain text: "what labs are available" — should return real data from backend
7. Click inline keyboard buttons — should trigger predefined queries

### Troubleshooting

**Bot not starting:**
```bash
docker compose logs bot
```

Check for:
- Missing environment variables
- Invalid BOT_TOKEN
- LLM API connection errors

**Backend unreachable from bot:**
The bot uses `http://backend:8000` (Docker network service name), not `localhost`. Verify the bot service is on the `lms-network`.

**LLM returns 500 errors:**
The Qwen Code API proxy needs valid OAuth credentials. Restart the proxy:
```bash
cd ~/qwen-code-oai-proxy && docker compose restart
```

### Stop and remove

```bash
# Stop the bot
docker compose stop bot

# Remove the bot container
docker compose rm -f bot

# Rebuild from scratch
docker compose down bot
docker compose up --build -d bot
```
