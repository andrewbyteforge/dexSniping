"""
Simple Test Server
File: test_server.py

A minimal server to test if we can serve the dashboard.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Dashboard Test")

# Mount static files
if Path("frontend/static").exists():
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple root endpoint."""
    return HTMLResponse("""
    <html>
    <body style="padding: 50px; font-family: Arial;">
        <h1>Test Server Running!</h1>
        <p>Server is accessible at http://127.0.0.1:8000</p>
        <p><a href="/dashboard">Go to Dashboard</a></p>
    </body>
    </html>
    """)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the dashboard with sidebar."""
    try:
        return templates.TemplateResponse(
            "pages/dashboard.html",
            {"request": request}
        )
    except Exception as e:
        return HTMLResponse(f"""
        <html>
        <body style="padding: 50px;">
            <h1>Dashboard Error</h1>
            <p>Error: {e}</p>
            <p>Template path: frontend/templates/pages/dashboard.html</p>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    print("Starting test server...")
    print("Dashboard: http://127.0.0.1:8000/dashboard")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
