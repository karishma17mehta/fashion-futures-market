# Fashion Futures Market

A prediction market for fashion micro-trends. Users trade on whether underground aesthetics will go mainstream. AI scrapes hyper-niche social signals and acts as market maker. Brands pay for the aggregated trend intelligence.

## How It Works

1. **Signal Engine** — scrapes Depop, Reddit, TikTok hashtags, Pinterest for emerging trend velocity
2. **AI Scoring** — Claude rates each signal on novelty + velocity, writes a trend thesis
3. **Prediction Markets** — each trend becomes a tradeable contract (YES/NO: will this go mainstream by X date?)
4. **Resolution Oracle** — Google Trends + brand homepage scraping determines if a trend "made it"
5. **Brand Intelligence** — aggregated crowdsourced predictions sold as trend forecasting data

## Stack

- **Frontend**: Next.js 14 + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + Redis
- **AI**: Claude API (Anthropic)
- **Auth**: Supabase

## Project Structure

```
fashion_tech/
├── frontend/          # Next.js app
│   └── src/
│       ├── app/       # App router pages
│       ├── components/
│       └── lib/       # API clients, utils
├── backend/
│   ├── api/           # FastAPI routes
│   ├── scrapers/      # Depop, Reddit, TikTok scrapers
│   ├── ai/            # Claude trend scoring
│   └── db/            # Models, migrations
└── data/
    └── seeds/         # Initial trend data
```

## Getting Started

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
