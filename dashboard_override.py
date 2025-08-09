"""
Dashboard Override
File: dashboard_override.py

Forces the correct dashboard to display.
"""

from pathlib import Path

def apply_override():
    """Apply the dashboard override to factory.py."""
    
    factory_path = Path("app/factory.py")
    if not factory_path.exists():
        print("Factory.py not found")
        return False
    
    with open(factory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import at the top if not present
    if 'from fastapi.templating import Jinja2Templates' not in content:
        content = 'from fastapi.templating import Jinja2Templates\n' + content
    
    # Find _setup_essential_routes function
    if 'def _setup_essential_routes' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'def _setup_essential_routes' in line:
                # Add our override after the function definition
                override_code = """
    # OVERRIDE: Force correct dashboard
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard_override(request: Request):
        templates = Jinja2Templates(directory="frontend/templates")
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
    
    @app.get("/", response_class=HTMLResponse)
    async def root_override(request: Request):
        templates = Jinja2Templates(directory="frontend/templates")
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
"""
                lines.insert(i + 2, override_code)
                content = '\n'.join(lines)
                break
    
    with open(factory_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Override applied!")
    return True

if __name__ == "__main__":
    apply_override()
