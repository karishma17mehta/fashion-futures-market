from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import trends, markets, users

app = FastAPI(title="Fashion Futures Market API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trends.router, prefix="/trends", tags=["trends"])
app.include_router(markets.router, prefix="/markets", tags=["markets"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/health")
def health():
    return {"status": "ok"}
