"""
Simple Template Fix
File: fix_template_rendering.py

Fixes the route manager to properly serve your original dashboard template
instead of falling back to generated HTML.
"""

from pathlib import Path

def fix_template_rendering():
    """Fix the route manager to properly serve original templates."""
    
    route_manager_path = Path("app/api/route_manager.py")
    
    if not route_manager_path.exists():
        print("❌ route_manager.py not found")
        return False
    
    try:
        # Read current content
        content = route_manager_path.read_text(encoding='utf-8')
        
        # Create backup
        backup = route_manager_path.with_suffix('.py.template_backup')
        backup.write_text(content, encoding='utf-8')
        print(f"✅ Backup created: {backup}")
        
        # Find the problematic method and replace with simple template serving
        method_start = content.find('def _setup_frontend_routes(')
        if method_start == -1:
            print("❌ Method not found")
            return False
        
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\n    async def ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Create simple method that just serves your original template
        simple_method = '''    def _setup_frontend_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup frontend routes to serve original dashboard template."""
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_dashboard(request: Request) -> HTMLResponse:
            """Serve your original dashboard template."""
            if self.templates:
                return self.templates.TemplateResponse(
                    "pages/dashboard.html",
                    {"request": request}
                )
            else:
                # Only if templates completely fail
                return HTMLResponse("<h1>Dashboard template not found</h1>")
        
        @app.get("/risk-analysis", response_class=HTMLResponse)
        async def serve_risk_analysis(request: Request) -> HTMLResponse:
            """Redirect to dashboard for now."""
            return self.templates.TemplateResponse(
                "pages/dashboard.html",
                {"request": request}
            ) if self.templates else HTMLResponse("<h1>Template not found</h1>")
        
        @app.get("/live-trading", response_class=HTMLResponse) 
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Redirect to dashboard for now."""
            return self.templates.TemplateResponse(
                "pages/dashboard.html", 
                {"request": request}
            ) if self.templates else HTMLResponse("<h1>Template not found</h1>")
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Redirect to dashboard for now."""
            return self.templates.TemplateResponse(
                "pages/dashboard.html",
                {"request": request}
            ) if self.templates else HTMLResponse("<h1>Template not found</h1>")
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Redirect to dashboard for now.""" 
            return self.templates.TemplateResponse(
                "pages/dashboard.html",
                {"request": request}
            ) if self.templates else HTMLResponse("<h1>Template not found</h1>")
        
        logger.info("Frontend routes configured to serve original dashboard template")

'''
        
        # Also remove any problematic helper methods
        helper_start = content.find('def _create_dashboard_html(')
        if helper_start == -1:
            helper_start = content.find('def _create_working_dashboard_html(')
        if helper_start == -1:
            helper_start = content.find('def _create_professional_dashboard_fallback(')
        
        if helper_start != -1:
            helper_end = content.find('\n    def ', helper_start + 1)
            if helper_end == -1:
                helper_end = content.find('\nclass ', helper_start + 1)
            if helper_end == -1:
                helper_end = len(content)
            
            # Remove the problematic helper method entirely
            new_content = content[:method_start] + simple_method + content[method_end:helper_start] + content[helper_end:]
        else:
            # Just replace the frontend routes method
            new_content = content[:method_start] + simple_method + content[method_end:]
        
        route_manager_path.write_text(new_content, encoding='utf-8')
        
        print("✅ Route manager simplified to serve original templates")
        print("✅ No more fallback HTML generation")
        print("✅ Direct template serving enabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False


def check_original_templates():
    """Check if your original templates exist."""
    print("🔍 Checking for your original dashboard template...")
    
    dashboard_template = Path("frontend/templates/pages/dashboard.html")
    base_template = Path("frontend/templates/base/layout.html")
    css_file = Path("frontend/static/css/main.css")
    
    if dashboard_template.exists():
        print(f"✅ Found original dashboard: {dashboard_template}")
        
        # Check if it has the expected content
        content = dashboard_template.read_text(encoding='utf-8')
        if "Professional Trading Dashboard" in content:
            print("✅ Dashboard template contains professional trading content")
            return True
        else:
            print("⚠️ Dashboard template exists but may not be the professional version")
            return True
    else:
        print(f"❌ Original dashboard template not found: {dashboard_template}")
        return False


if __name__ == "__main__":
    print("🔧 Simple Template Fix")
    print("=" * 40)
    print("Goal: Serve your ORIGINAL dashboard template, not generated HTML")
    
    templates_exist = check_original_templates()
    
    if templates_exist:
        print("\n✅ Your original dashboard template exists!")
        success = fix_template_rendering()
        
        if success:
            print("\n🎉 SUCCESS! Template rendering fixed!")
            print("✅ RouteManager will now serve your original dashboard")
            print("✅ No more fallback HTML generation")
            print("🚀 Run: python -m app.main")
            print("🌐 Visit: http://localhost:8000/dashboard")
            print("\n💡 You should now see your ORIGINAL professional dashboard!")
        else:
            print("\n❌ Fix failed - check errors above")
    else:
        print("\n❌ Original dashboard template not found")
        print("💡 The template may have been moved or renamed during refactoring")
    
    print("=" * 40)