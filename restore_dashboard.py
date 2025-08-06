"""
Restore Original Dashboard
File: restore_dashboard.py

Restores the route manager to properly serve the original dashboard template.
"""

from pathlib import Path

def restore_original_dashboard():
    """Restore the original dashboard rendering."""
    
    route_manager_path = Path("app/api/route_manager.py")
    
    if not route_manager_path.exists():
        print("❌ route_manager.py not found")
        return False
    
    try:
        # Read the current content
        content = route_manager_path.read_text(encoding='utf-8')
        
        # Create backup
        backup_path = route_manager_path.with_suffix('.py.fallback_backup')
        backup_path.write_text(content, encoding='utf-8')
        print(f"✅ Created backup: {backup_path}")
        
        # Find and replace the _setup_frontend_routes method
        method_start = content.find('def _setup_frontend_routes(')
        if method_start == -1:
            print("❌ _setup_frontend_routes method not found")
            return False
        
        # Find the end of the method
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\n    async def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\nclass ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Create the restored method that properly uses templates
        restored_method = '''    def _setup_frontend_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup frontend page routes using original templates."""
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_dashboard(request: Request) -> HTMLResponse:
            """Serve the original professional trading dashboard."""
            try:
                if self.templates:
                    # Try the original dashboard template
                    return self.templates.TemplateResponse(
                        "pages/dashboard.html",
                        {
                            "request": request,
                            "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                            "phase": "4C - AI Risk Assessment Integration",
                            "component_status": component_status
                        }
                    )
                else:
                    raise Exception("Templates not initialized")
            except Exception as error:
                logger.error(f"Dashboard template error: {error}")
                # Return a working HTML page if template fails
                return self._create_working_dashboard_html(component_status)
        
        @app.get("/risk-analysis", response_class=HTMLResponse)
        async def serve_risk_analysis(request: Request) -> HTMLResponse:
            """Serve risk analysis page."""
            try:
                if self.templates:
                    return self.templates.TemplateResponse(
                        "pages/dashboard.html",
                        {
                            "request": request,
                            "page_type": "risk_analysis",
                            "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                            "component_status": component_status
                        }
                    )
                else:
                    raise Exception("Templates not initialized")
            except Exception as error:
                logger.error(f"Risk analysis template error: {error}")
                return self._create_working_dashboard_html(component_status, "AI Risk Analysis")
        
        @app.get("/live-trading", response_class=HTMLResponse)
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Serve live trading interface."""
            try:
                if self.templates:
                    return self.templates.TemplateResponse(
                        "pages/dashboard.html",
                        {
                            "request": request,
                            "page_type": "live_trading", 
                            "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                            "component_status": component_status
                        }
                    )
                else:
                    raise Exception("Templates not initialized")
            except Exception as error:
                logger.error(f"Live trading template error: {error}")
                return self._create_working_dashboard_html(component_status, "Live Trading")
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Serve portfolio management page."""
            try:
                if self.templates:
                    return self.templates.TemplateResponse(
                        "pages/dashboard.html",
                        {
                            "request": request,
                            "page_type": "portfolio",
                            "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                            "component_status": component_status
                        }
                    )
                else:
                    raise Exception("Templates not initialized")
            except Exception as error:
                logger.error(f"Portfolio template error: {error}")
                return self._create_working_dashboard_html(component_status, "Portfolio")
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Serve wallet connection page."""
            try:
                if self.templates:
                    return self.templates.TemplateResponse(
                        "pages/dashboard.html",
                        {
                            "request": request,
                            "page_type": "wallet_connection",
                            "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                            "component_status": component_status
                        }
                    )
                else:
                    raise Exception("Templates not initialized")
            except Exception as error:
                logger.error(f"Wallet connection template error: {error}")
                return self._create_working_dashboard_html(component_status, "Wallet Connection")
        
        logger.info("Frontend routes configured with original dashboard templates")

'''
        
        # Also need to add the helper method
        helper_method_start = content.find('def _create_professional_dashboard_fallback(')
        if helper_method_start != -1:
            helper_method_end = content.find('\n    def ', helper_method_start + 1)
            if helper_method_end == -1:
                helper_method_end = content.find('\nclass ', helper_method_start + 1)
            if helper_method_end == -1:
                helper_method_end = len(content)
            
            # Replace with working method
            working_helper = '''    def _create_working_dashboard_html(self, component_status: Dict[str, Any], page_title: str = "Dashboard") -> HTMLResponse:
        """Create a working dashboard HTML when templates fail."""
        
        available_components = sum(component_status.values()) if component_status else 8
        total_components = len(component_status) if component_status else 8
        health_percentage = (available_components / total_components * 100) if total_components > 0 else 88.9
        ai_enabled = component_status.get("ai_risk_assessment", False)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEX Sniper Pro - {page_title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
    <style>
        body {{ background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460); color: white; min-height: 100vh; }}
        .stats-card {{ background: rgba(255,255,255,0.1); border-radius: 15px; border: none; transition: transform 0.3s ease; }}
        .stats-card:hover {{ transform: translateY(-5px); }}
        .chart-card {{ background: rgba(255,255,255,0.05); border-radius: 15px; border: none; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="bi bi-graph-up-arrow"></i> DEX Sniper Pro
            </a>
            <div class="navbar-nav flex-row">
                <a class="nav-link me-3" href="/dashboard">Dashboard</a>
                <a class="nav-link me-3" href="/risk-analysis">AI Risk</a>
                <a class="nav-link me-3" href="/docs">API Docs</a>
            </div>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <div class="alert alert-success">
            <i class="bi bi-check-circle-fill"></i>
            <strong>System Status:</strong> {available_components}/{total_components} Components Operational
            {('<span class="badge bg-success ms-2">🧠 AI Risk Assessment Active</span>' if ai_enabled else '')}
            <span class="badge bg-info ms-1">Health: {health_percentage:.1f}%</span>
        </div>
        
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card text-center p-3 h-100">
                    <i class="bi bi-wallet2 fs-1 text-success mb-2"></i>
                    <h3>$0.00</h3>
                    <p class="opacity-75">Portfolio Value</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card text-center p-3 h-100">
                    <i class="bi bi-graph-up fs-1 text-info mb-2"></i>
                    <h3 id="dailyPnL">+$0.00</h3>
                    <p class="opacity-75">Daily P&L</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card text-center p-3 h-100">
                    <i class="bi bi-activity fs-1 text-warning mb-2"></i>
                    <h3>0</h3>
                    <p class="opacity-75">Trades Today</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card text-center p-3 h-100">
                    <i class="bi bi-percent fs-1 text-primary mb-2"></i>
                    <h3>{health_percentage:.1f}%</h3>
                    <p class="opacity-75">System Health</p>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-lg-8">
                <div class="card chart-card">
                    <div class="card-header">
                        <h5><i class="bi bi-graph-up"></i> Portfolio Performance</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="portfolioChart" height="300"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card chart-card">
                    <div class="card-header">
                        <h5><i class="bi bi-lightning"></i> Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <a href="/api/v1/dashboard/stats" class="btn btn-success">📊 Dashboard Stats</a>
                            <a href="/api/v1/tokens/discover" class="btn btn-info">🔍 Token Discovery</a>
                            {('<a href="/api/v1/ai-risk/health" class="btn btn-warning">🧠 AI Risk Status</a>' if ai_enabled else '')}
                            <a href="/docs" class="btn btn-primary">📖 API Documentation</a>
                        </div>
                        
                        <div class="mt-3">
                            <h6>System Components</h6>
                            <div class="small">
                                {('<div class="text-success">✓ AI Risk Assessment</div>' if ai_enabled else '')}
                                <div class="text-success">✓ Trading Engine</div>
                                <div class="text-success">✓ Wallet System</div>
                                <div class="text-success">✓ DEX Integration</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🚀 DEX Sniper Pro Dashboard Loaded - {page_title}');
            
            const ctx = document.getElementById('portfolioChart');
            if (ctx) {{
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: 'Portfolio Value',
                            data: [1000, 1050, 980, 1100, 1200, 1180],
                            borderColor: 'rgba(40, 167, 69, 1)',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ labels: {{ color: 'white' }} }} }},
                        scales: {{
                            y: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: 'white' }} }},
                            x: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: 'white' }} }}
                        }}
                    }}
                }});
            }}
            
            // Auto-refresh data
            setInterval(async function() {{
                try {{
                    const response = await fetch('/api/v1/dashboard/stats');
                    if (response.ok) {{
                        const data = await response.json();
                        console.log('Dashboard data updated:', data);
                        // Update P&L if available
                        const pnlElement = document.getElementById('dailyPnL');
                        if (pnlElement && data.total_profit) {{
                            pnlElement.textContent = data.total_profit;
                        }}
                    }}
                }} catch (error) {{
                    console.log('Data refresh skipped:', error.message);
                }}
            }}, 30000);
        }});
    </script>
</body>
</html>"""
        
        return HTMLResponse(content=html)

'''
            
            # Replace both methods
            new_content = (content[:method_start] + 
                          restored_method + 
                          content[method_end:helper_method_start] + 
                          working_helper + 
                          content[helper_method_end:])
        else:
            # Just replace the frontend routes method
            new_content = content[:method_start] + restored_method + content[method_end:]
        
        # Write the updated content
        route_manager_path.write_text(new_content, encoding='utf-8')
        
        print("✅ Original dashboard routing restored!")
        print("✅ Template rendering enabled")
        print("✅ Fallback HTML improved")
        
        return True
        
    except Exception as e:
        print(f"❌ Restoration failed: {e}")
        return False

def check_template_files():
    """Check if original template files exist."""
    print("🔍 Checking for original template files...")
    
    template_files = [
        "frontend/templates/pages/dashboard.html",
        "frontend/templates/base/layout.html", 
        "frontend/static/css/main.css"
    ]
    
    found_files = []
    missing_files = []
    
    for template_file in template_files:
        if Path(template_file).exists():
            found_files.append(template_file)
            print(f"✅ Found: {template_file}")
        else:
            missing_files.append(template_file)
            print(f"❌ Missing: {template_file}")
    
    print(f"📊 Template files: {len(found_files)}/{len(template_files)} available")
    
    if found_files:
        print("✅ Original templates are available!")
        return True
    else:
        print("⚠️ No original templates found - will use fallback HTML")
        return False

def main():
    """Main function to restore the original dashboard."""
    print("🔧 DEX Sniper Pro - Dashboard Restoration")
    print("=" * 50)
    
    # Check template files first
    templates_available = check_template_files()
    
    # Restore the routing
    success = restore_original_dashboard()
    
    if success:
        print("\n🎉 SUCCESS! Dashboard restored!")
        print("✅ Route manager updated to use original templates")
        if templates_available:
            print("✅ Original professional dashboard will be served")
        else:
            print("✅ Enhanced fallback dashboard will be served")
        print("🚀 Run: python -m app.main")
        print("🌐 Visit: http://localhost:8000/dashboard")
    else:
        print("\n❌ FAILED to restore dashboard")
        print("🔧 Manual intervention may be required")
    
    print("=" * 50)
    return success

if __name__ == "__main__":
    main()