import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings, validate_settings
from .routers import audit, auth, dashboard, taxpayers, transactions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
validate_settings(settings)

app = FastAPI(
    title="TaxWatch API",
    version="1.0.0",
    description="Regional tax transaction monitoring: taxpayers, transactions, anomalies, audit.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
for module in (auth, taxpayers, transactions, dashboard, audit):
    app.include_router(module.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
