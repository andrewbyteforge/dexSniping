"""
Restore Original Routes
File: restore_original_routes.py

This restores the original simple route setup that was working before
the Phase 4C refactoring complicated things.
"""

from pathlib import Path

def restore_original_routes():
    """Restore the original route setup that was working."""
    
    # Check if original dashboard exists
    dashboard_path = Path("frontend/templates/pages/dashboard.html")
    if not dashboard_path.exists():
        print("❌ Original dashboard template not found")
        return False
    
    print("✅ Original dashboard template found")
    
    # Replace the RouteManager's _setup_frontend_routes with the original working version
    route_manager_path = Path("app/api/route_manager.py")
    
    if not route_manager_path.exists():
        print("❌ RouteManager not found")
        return False
    
    try:
        content = route_manager_path.read_text(encoding='utf-8')
        
        # Backup
        backup = route_manager_path.with_suffix('.py.original_backup')
        backup.write_text(content, encoding='utf-8')
        print(f"✅ Backup created: {backup}")
        
        # Find and replace the problematic method with the ORIGINAL working version
        method_start = content.find('def _setup_frontend_routes(')
        if method_start == -1:
            print("❌ Method not found")
            return False
        
        # Find method end
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\n    async def ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Use the ORIGINAL working route setup - simple and clean
        original_working_method = '''    def _setup_frontend_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup frontend routes using the ORIGINAL working template approach."""
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_dashboard(request: Request) -> HTMLResponse:
            """Serve the main trading dashboard - ORIGINAL VERSION."""
            try:
                if self.templates:
                    return self.templates.TemplateResponse(
                        "pages/dashboard.html", 
                        {"request": request}
                    )
                else:
                    raise Exception("Templates not initialized")
            except Exception as error:
                logger.error(f"Dashboard template error: {error}")
                # Simple error response instead of complex fallback
                return HTMLResponse(
                    content=f"<h1>Dashboard Error</h1><p>{error}</p>",
                    status_code=500
                )
        
        @app.get("/", response_class=HTMLResponse)  
        async def root_redirect(request: Request) -> HTMLResponse:
            """Root redirect to dashboard - ORIGINAL VERSION."""
            return await serve_dashboard(request)
        
        @app.get("/risk-analysis", response_class=HTMLResponse)
        async def serve_risk_analysis(request: Request) -> HTMLResponse:
            """Serve risk analysis - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        @app.get("/live-trading", response_class=HTMLResponse)
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Serve live trading - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Serve portfolio - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Serve wallet connection - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        logger.info("Frontend routes configured with ORIGINAL template approach")

'''
        
        # Remove any problematic helper methods that generate HTML
        helper_methods_to_remove = [
            'def _create_dashboard_html(',
            'def _create_working_dashboard_html(',  
            'def _create_professional_dashboard_fallback('
        ]
        
        new_content = content[:method_start] + original_working_method + content[method_end:]
        
        # Remove problematic helper methods
        for helper_method in helper_methods_to_remove:
            helper_start = new_content.find(helper_method)
            if helper_start != -1:
                # Find end of this helper method
                helper_end = new_content.find('\n    def ', helper_start + 1)
                if helper_end == -1:
                    helper_end = new_content.find('\n    async def ', helper_start + 1)
                if helper_end == -1:
                    helper_end = new_content.find('\nclass ', helper_start + 1)
                if helper_end == -1:
                    helper_end = len(new_content)
                
                # Remove this helper method
                new_content = new_content[:helper_start] + new_content[helper_end:]
                print(f"✅ Removed problematic helper method: {helper_method}")
        
        # Write the cleaned content
        route_manager_path.write_text(new_content, encoding='utf-8')
        
        print("✅ Restored ORIGINAL working route setup")
        print("✅ Removed all complex HTML generation methods")
        print("✅ Simple template serving restored")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to restore routes: {e}")
        return False


def check_dashboard_content():
    """Check the original dashboard content."""
    dashboard_path = Path("frontend/templates/pages/dashboard.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard template not found")
        return False
    
    try:
        content = dashboard_path.read_text(encoding='utf-8')
        print(f"✅ Dashboard template found: {len(content)} characters")
        
        # Check for key elements of your original dashboard
        key_elements = [
            "Professional Trading Dashboard",
            "Portfolio Value", 
            "Daily P&L",
            "extends \"base/layout.html\"",
            "Chart.js",
            "loadDashboardStats",
            "updateDashboardStats"
        ]
        
        found_elements = []
        for element in key_elements:
            if element in content:
                found_elements.append(element)
        
        print(f"✅ Found {len(found_elements)}/{len(key_elements)} key dashboard elements:")
        for element in found_elements:
            print(f"   ✓ {element}")
        
        if len(found_elements) >= 4:
            print("✅ This appears to be your original professional dashboard!")
            return True
        else:
            print("⚠️ This may not be the complete original dashboard")
            return True
            
    except Exception as e:
        print(f"❌ Error reading dashboard: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Restore Original Dashboard Routes")
    print("=" * 50)
    print("Goal: Go back to the ORIGINAL working route setup")
    print("Stop using complex HTML generation, just serve your template!")
    
    # Check dashboard first
    dashboard_ok = check_dashboard_content()
    
    if dashboard_ok:
        print("\n✅ Original dashboard template looks good!")
        
        # Restore original routes
        success = restore_original_routes()

        if success:
            print("\n🎉 SUCCESS! Original routes restored!")
            print("✅ Using ORIGINAL simple template serving approach")
            print("✅ No more complex HTML generation")
            print("✅ Direct template rendering like before")
            print("\n🚀 Run: python -m app.main")
            print("🌐 Visit: http://localhost:8000/dashboard")
            print("\n💡 You should now see your ORIGINAL dashboard!")
            print("💡 The same one that was working before Phase 4C!")
        else:
            print("\n❌ Failed to restore routes")
    else:
        print("\n❌ Dashboard template issues detected")

    print("=" * 50)
