# Fashion Futures Market

A prediction market for fashion micro-trends. Users trade on whether underground aesthetics will go mainstream before they actually do. A deterministic scoring engine ingests signals from across the social and editorial web, Claude writes the investment thesis, and every trend becomes a tradeable YES/NO contract. The aggregated, crowd-priced predictions are the product — sold to brands as forward-looking trend intelligence.

> **Status:** Functional end-to-end. ~315 trends and markets seeded from live scrapers, weekly autonomous pipeline, gamified trading, and a brand-facing signals API. Preparing first public deploy.

---

## How It Works

1. **Signal Engine** — scrapes editorial RSS (Vogue, WWD, Harper's, Refinery29, Elle), Reddit, TikTok, Pinterest, and Google Trends for emerging trend velocity.
2. **Deterministic Scoring** — a transparent formula scores each signal on velocity, novelty, acceleration, volume, and cross-platform confirmation (`scoring/formula.py`). No LLM-generated numbers — Claude only writes the narrative thesis.
3. **Cross-Platform Confirmation** — when the same trend surfaces on multiple sources, its score is boosted and it's tagged "cross-confirmed." A trend seen on TikTok + Editorial + Reddit is a stronger signal than one seen once.
4. **Prediction Markets** — each trend becomes a tradeable contract priced by an LMSR market maker (*"Will sheer layering be everywhere this summer?"* → YES/NO).
5. **Auto-Resolution Agent** — when a market expires, an agent gathers real-world evidence (Google Trends peak, editorial mentions, score trajectory) and resolves YES/NO/extend automatically.
6. **Gamification** — traders earn XP and badges for early calls, correct predictions, streaks, and cross-platform foresight. Ranks: Novice → Forecaster → Oracle → Legend.
7. **Brand Intelligence API** — aggregated crowd predictions and cross-platform signals exposed via a read API for brand/forecasting customers.

---

## Stack

- **Frontend**: Next.js 16 (App Router) + Tailwind CSS v4
- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL (Redis configured for future use)
- **AI**: Claude API (Anthropic) — thesis generation only
- **Scheduling**: cron → weekly autonomous agent run

---

## Project Structure

```
fashion_tech/
├── frontend/                  # Next.js 16 app
│   ├── app/
│   │   ├── page.tsx           # Markets homepage (signal ticker, hottest market)
│   │   ├── trends/            # Signal index + trend detail (score breakdown, sparkline)
│   │   ├── markets/           # Market detail + trading
│   │   ├── portfolio/         # Positions & P&L
│   │   ├── alerts/            # Trend alert subscriptions
│   │   ├── leaderboard/       # XP / accuracy leaderboard
│   │   └── about/
│   ├── components/            # SourceBadge, ScoreBreakdown, SignalTicker, etc.
│   └── lib/api.ts             # Backend API client (NEXT_PUBLIC_API_URL)
│
├── backend/
│   ├── api/
│   │   └── routes/            # trends, markets, users, signals (brand API), alerts
│   ├── scrapers/              # editorial RSS, reddit, tiktok, pinterest, google trends
│   │   └── pipeline.py        # scrape → score → upsert trends & markets
│   ├── scoring/               # deterministic feature extraction + scoring formula
│   ├── ai/                    # Claude thesis generation
│   ├── agents/                # autonomous agents (see below)
│   ├── db/                    # SQLAlchemy models + session
│   ├── data/
│   │   ├── seeds/             # manual seed data
│   │   └── snapshots/         # seed_dump.sql (portable DB snapshot for deploy)
│   └── scripts/               # one-off maintenance (e.g. rewrite_markets.py)
│
└── docker-compose.yml         # local Postgres + Redis
```

---

## Autonomous Agents

Run individually or orchestrated together via `agents/run_all.py` (wired to weekly cron).

| Agent | What it does |
|---|---|
| `pipeline.py` | Scrape all sources, score signals, **upsert** trends (updates existing, no duplicates) |
| `score_decay.py` | Decay stale scores over time; apply cross-platform confirmation boosts |
| `auto_resolve.py` | Resolve expired markets from real-world evidence; pay out winners |
| `gamification.py` | Award XP, grant badges, track streaks, promote ranks |
| `weekly_digest.py` | Compile a weekly summary (new trends, movers, resolutions) |
| `alert_dispatcher.py` | Fire user trend-alert notifications (email via SMTP if configured) |
| `run_all.py` | Orchestrate all of the above in order |

```bash
# Full weekly run
python -m agents.run_all

# Safe dry run (no DB writes, no emails)
python -m agents.run_all --skip-scrape --dry-run

# Test auto-resolution logic on N random markets (never writes)
python -m agents.auto_resolve --force-test 5
```

The weekly cron (`cron_weekly.sh`) runs the full orchestration every Sunday at 6am.

---

## API Highlights

Interactive docs at `/docs` when the backend is running.

```
GET  /trends/                      # all trends (score, source, cross-platform info)
GET  /markets/?status=open         # tradeable markets with live prices
GET  /users/{id}/positions         # enriched positions with P&L
GET  /users/leaderboard            # XP + accuracy ranked
GET  /users/{id}/badges            # earned badges

# Brand intelligence API
GET  /signals/top                  # top signals (filter by score, source, cross-platform)
GET  /signals/cross-platform       # only multi-source confirmed trends
GET  /signals/digest               # weekly digest
GET  /signals/score-history/{id}   # score over time (sparkline data)

# Alert subscriptions
POST /alerts/                       # subscribe to a trend / score threshold
GET  /alerts/{user_id}              # list subscriptions
```

---

## Getting Started (Local)

### 1. Start Postgres + Redis
```bash
docker-compose up -d
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure secrets
cp .env.example .env   # then fill in ANTHROPIC_API_KEY, REDDIT_*, DATABASE_URL

# Create tables + load seed data
psql "$DATABASE_URL" < data/snapshots/seed_dump.sql

uvicorn api.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Open **http://localhost:3000** for the app and **http://localhost:8000/docs** for the API.

---

## Environment Variables

**Backend** (`backend/.env`)
| Var | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Claude API key (thesis generation) |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | Reddit scraper |
| `FRONTEND_ORIGINS` | Comma-separated allowed CORS origins (your deployed frontend URL) |
| `SMTP_*` / `DIGEST_EMAIL` | *(optional)* email alerts & weekly digest |

**Frontend** (`frontend/.env.local`)
| Var | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend base URL |

---

## Deployment

- **Frontend** → Vercel (root directory `frontend`, set `NEXT_PUBLIC_API_URL`)
- **Backend + Postgres** → Railway (root directory `backend`; `Procfile` + `runtime.txt` included)
- Load `backend/data/snapshots/seed_dump.sql` into the cloud Postgres to seed trends & markets.

CORS is env-driven (`FRONTEND_ORIGINS`) and automatically allows `*.vercel.app` preview deploys.
