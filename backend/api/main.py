import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import trends, markets, users, signals, alerts, auth, reports

app = FastAPI(title="Fashion Futures Market API", version="0.1.0")

# Allowed origins: localhost for dev, plus any comma-separated domains in the
# FRONTEND_ORIGINS env var (set this to your Vercel URL in production).
_default_origins = ["http://localhost:3000"]
_env_origins = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _env_origins,
    # Also allow any *.vercel.app preview deployment
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,   prefix="/auth",   tags=["auth"])
app.include_router(trends.router, prefix="/trends", tags=["trends"])
app.include_router(markets.router, prefix="/markets", tags=["markets"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(signals.router, prefix="/signals", tags=["brand-api"])
app.include_router(alerts.router,  prefix="/alerts",  tags=["alerts"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])


@app.get("/health")
def health():
    return {"status": "ok"}
