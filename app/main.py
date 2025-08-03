from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="DEX Sniper Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="frontend/templates")

if Path("frontend/static").exists():
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include both API routers
from app.api.v1.endpoints.dashboard import dashboard_router, tokens_router
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(tokens_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "🤖 DEX Sniper Pro Trading Bot API",
        "version": "1.0.0",
        "status": "running",
        "dashboard": "/dashboard",
        "docs": "/docs"
    }

@app.get("/dashboard")
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})

# Sidebar navigation - all redirect to dashboard for now
@app.get("/token-discovery")
async def token_discovery(request: Request):
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})

@app.get("/live-trading")
async def live_trading(request: Request):
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})

@app.get("/portfolio")
async def portfolio(request: Request):
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})