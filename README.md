# AI Impact Monitor Backend

Backend service for the **[AI Impact Monitor](https://github.com/Sjoerd473/AI_monitor_plugin) Chrome extension**, which tracks the environmental footprint (CO₂, energy, water) of AI usage on ChatGPT, Claude, Gemini, and Perplexity.

This FastAPI‑based API:

- Ingests anonymized prompt‑event metadata from the extension.
- Stores data in PostgreSQL and buffers inserts via Redis for efficiency.
- Computes environmental metrics and serves a dashboard UI with charts.
- Follows a **privacy‑first**, opt‑in‑for‑research model.

## Features

- **Event‑driven ingestion**:
  - Extension sends anonymized events to `POST /events` using a `Bearer` token.
  - Events are queued in Redis (`event_queue`) and batch‑inserted into PostgreSQL.
- **User & token management**:
  - `POST /register` creates a local user ID and returns a bearer token.
  - Tokens are stored as SHA‑256 hashes; no plaintext tokens are persisted.
- **Rate limiting**:
  - Sliding‑window per‑token rate‑limit using Redis ZSET (e.g., 20 requests / 60s).
  - IP‑based rate‑limit for registration (`/register`).
- **Dashboard & metrics**:
  - Real‑time environmental stats: CO₂ emissions (g), energy (Wh), and water (L).
  - Charts comparing **current vs. previous** periods (hour / day / week).
  - Drill‑down by **category** (e.g., `coding`, `creative`) and **model**.
- **Research‑oriented exports** (optional):
  - Periodic JSON dumps (`prompt_dump`) for later analysis.
  - Commented download endpoint (`/download/dataset`) for researcher‑facing access.

## Architecture

### Services

- `ai-monitor` (FastAPI)
  - Async service built with `FastAPI`, `psycopg_pool`, Redis, and APScheduler.
  - Lifespan worker:
    - `flush_worker` consumes `event_queue` and batches inserts into `PromptDB.insert_prompts`.
    - `generate_prompt_data` dumps JSON snapshots on a cron‑style schedule.
- `db` (PostgreSQL 16‑alpine)
  - Stores users, tokens, sessions, prompts, responses, environment, UI interactions, and conversations.
- `redis` (Redis 7‑alpine)
  - Event queue and rate‑limit buckets.
- `nginx` (NGINX‑alpine)
  - Reverse proxy in front of `ai-monitor`, terminating TLS with Let’s Encrypt.
  - Exposes `80` / `443` and routes to `ai-monitor:5000`.

### Data Flow

1. Extension detects a prompt → local tracking + optional `data_sharing` opt‑in.
2. Extension sends event to `https://ai-monitor.madebyshu.net/events` with `Authorization: Bearer <token>`.
3. FastAPI validates token and inserts into Redis list `event_queue`.
4. `flush_worker` reads from `event_queue` and writes batches to PostgreSQL via `PromptDB.insert_prompts`.
5. `generate_prompt_data` periodically writes JSON‑formatted dashboard data to `protected/data/dashboard.json`.
6. Dashboard page (`/dashboard`) fetches JSON and renders charts via Chart.js.

## Docker Compose Setup

This project uses `docker-compose.yaml` to orchestrate:

- `ai-monitor` (FastAPI + Gunicorn + Uvicorn worker).
- `db` (PostgreSQL).
- `redis` (Redis).
- `nginx` (with Let’s Encrypt certificates).

### Prerequisites

- Docker + Docker Compose.
- `docker` context running on a machine with ports `80` and `443` exposed.
- Environment file `.env` with DB credentials and any other variables.

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Sjoerd473/ai-impact-monitor-backend
cd ai-impact-monitor-backend

# 2. Copy and edit .env
cp .env.example .env
nano .env  # or vim / VS Code

# 3. Start the stack
docker compose up --build -d
```

Services will be available at:

- Backend: `http://127.0.0.1:80` (or your domain via NGINX + Let’s Encrypt).
- Dashboard: `https://ai-monitor.madebyshu.net/dashboard`.

### Example Environment Variables

`.env` should contain at least:

```bash
# PostgreSQL
POSTGRES_DB=aim_monitor
POSTGRES_USER=aim_user
POSTGRES_PASSWORD=your_secure_password

# FastAPI / Gunicorn
# GUNICORN_WORKER_ID=0  # for scheduler worker coordination
```

## API Endpoints

| Method | Path                         | Purpose |
|--------|------------------------------|---------|
| `POST` | `/register`                  | Register user; return `Bearer` token (IP‑rate‑limited). |
| `POST` | `/events`                    | Log prompt events (token‑rate‑limited, queued in Redis, then batch‑inserted). |
| `GET`  | `/`                          | Redirects to or serves the index page. |
| `GET`  | `/dashboard`                 | Dashboard UI with interactive charts. |
| `GET`  | `/data/dashboard.json`       | JSON‑based metrics for charts (CO₂, energy, water over time and by category/model). |
| `GET`  | `/privacy`                   | Privacy policy page. |
| `GET`  | `/download/dataset` (opt‑in) | Download anonymized research dataset ZIP (if enabled). |

## Privacy & Data Policy

- **No text collected**:
  - The extension and backend never store or transmit the actual text of prompts or responses.
- **Anonymization**:
  - User IDs are generated locally via `crypto.getRandomValues` and stored only as internal identifiers.
  - Tokens are hashed with SHA‑256 before storage.
- **Opt‑in research**:
  - Data sharing is off by default; users must explicitly enable it in the extension onboarding.
- **Retention & deletion**:
  - Users can request deletion of their data via the extension / backend (policy can be extended as needed).

## Dashboard & Charts

The frontend renders:

- Comparison charts (current vs. previous period) for:
  - CO₂ emissions (g).
  - Energy consumption (Wh).
  - Water usage (L).
- Charts grouped by **category** (e.g., `coding`, `creative`) and **model**.
- Configurable default visible categories via `DEFAULT_VISIBLE_CATEGORIES` in the JS code.

Charts are powered by Chart.js and consume JSON from:

- `/data/dashboard.json` (loaded into `fetchData` and `initDashboard`).

## Contributing

Contributions are welcome! Please:

- Open an issue to discuss large changes or new features.
- Fork the repo, add tests where relevant, and submit a pull request.
- Ensure any new endpoints or data collection respects the privacy‑first design.

## License

This project is licensed under the **Apache 2.0 License** – see the [LICENSE](LICENSE) file for details.

Developed by **[Your Name / Studio Name]**  
AI Impact Monitor: `ai-monitor.madebyshu.net`