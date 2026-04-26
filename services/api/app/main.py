from __future__ import annotations

from fastapi import FastAPI

from app.routers import scans

app = FastAPI(
    title="MDMScan API",
    description="Docker image security assessment REST API",
    version="0.1.0",
)

app.include_router(scans.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
