from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query
import random

# Dashboard router
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@dashboard_router.get("/stats")
async def get_dashboard_stats():
    return {
        "portfolio_value": 25000.50,
        "daily_pnl": 1250.75,
        "success_rate": 87.5,
        "trades_today": 23,
        "uptime_percent": 99.8
    }

# Tokens router (separate - matches dashboard expectation)
tokens_router = APIRouter(prefix="/tokens", tags=["tokens"])

@tokens_router.get("/discover")
async def get_tokens(
    limit: int = Query(10), 
    offset: int = Query(0), 
    sort: str = Query("age"), 
    order: str = Query("desc")
):
    tokens = []
    for i in range(limit):
        tokens.append({
            "symbol": f"TOKEN{i+1}",
            "price": round(random.uniform(0.001, 10), 4),
            "price_change_24h": round(random.uniform(-50, 100), 2),
            "liquidity_usd": random.randint(10000, 500000),
            "age": f"{random.randint(1, 24)}h",
            "risk_score": round(random.uniform(1, 10), 1)
        })
    return {"tokens": tokens}

# Export both routers
router = dashboard_router  # Keep this for compatibility