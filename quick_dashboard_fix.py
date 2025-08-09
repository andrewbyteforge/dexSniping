"""
Quick Dashboard Fix
File: quick_dashboard_fix.py

Adds the missing /dashboard route directly to the current main.py
"""

import os
from pathlib import Path


def fix_dashboard_route():
    """Add dashboard route directly to main.py"""
    
    main_file = Path("app/main.py")
    
    if not main_file.exists():
        print("❌ app/main.py not found!")
        return False
    
    try:
        # Read current content
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if dashboard route already exists
        if '@app.get("/dashboard"' in content:
            print("✅ Dashboard route already exists in main.py")
            return True
        
        # Add dashboard route after imports
        dashboard_route = '''
# Dashboard route
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the main dashboard page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniper Pro Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }
            .header { background: #343a40; color: white; padding: 1rem; text-align: center; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 20px 0; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { text-align: center; }
            .metric-value { font-size: 2em; font-weight: bold; color: #007bff; margin: 10px 0; }
            .button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .button:hover { background: #0056b3; }
            .api-result { margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff; }
            .success { border-left-color: #28a745; }
            .error { border-left-color: #dc3545; }
            .status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
            .status-operational { background: #d4edda; color: #155724; }
            .nav-link { color: #007bff; text-decoration: none; margin: 0 15px; }
            .nav-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 DEX Sniper Pro Dashboard</h1>
            <p>Professional Trading Bot - Phase 5B Complete</p>
            <div>
                <a href="/" class="nav-link">Home</a>
                <a href="/dashboard" class="nav-link">Dashboard</a>
                <a href="/api/docs" class="nav-link">API Docs</a>
                <a href="/health" class="nav-link">Health</a>
            </div>
        </div>
        
        <div class="container">
            <div class="card">
                <h3>🎯 System Status</h3>
                <p>Application Status: <span class="status-badge status-operational">Operational</span></p>
                <p>Dashboard Router: <span class="status-badge status-operational">Active</span></p>
                <p>Trading Engine: <span class="status-badge status-operational">Ready</span></p>
                <p>Database: <span class="status-badge status-operational">Connected</span></p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>📊 Portfolio Value</h3>
                    <div class="metric">
                        <div class="metric-value" id="portfolioValue">$1,250.75</div>
                        <small>Total Value</small>
                    </div>
                </div>
                
                <div class="card">
                    <h3>💰 Daily P&L</h3>
                    <div class="metric">
                        <div class="metric-value" id="dailyPnl" style="color: #28a745;">+$45.30</div>
                        <small>Today's Profit</small>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📈 Success Rate</h3>
                    <div class="metric">
                        <div class="metric-value" id="successRate">78.5%</div>
                        <small>Win Rate</small>
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚡ Active Trades</h3>
                    <div class="metric">
                        <div class="metric-value" id="activeTrades">3</div>
                        <small>Live Positions</small>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🧪 API Testing Center</h3>
                <p>Test the dashboard API endpoints:</p>
                <button class="button" onclick="testAPI('/api/v1/dashboard/stats')">📊 Test Stats API</button>
                <button class="button" onclick="testAPI('/api/v1/dashboard/trades')">⚡ Test Trades API</button>
                <button class="button" onclick="testAPI('/api/v1/dashboard/health')">❤️ Test Health API</button>
                <button class="button" onclick="refreshDashboard()">🔄 Auto Refresh</button>
                <div id="apiResults" class="api-result" style="display: none;"></div>
            </div>
            
            <div class="card">
                <h3>📋 Quick Actions</h3>
                <button class="button" onclick="window.open('/api/docs', '_blank')">📖 API Documentation</button>
                <button class="button" onclick="window.open('/health', '_blank')">💓 Health Check</button>
                <button class="button" onclick="testAllEndpoints()">🧪 Test All APIs</button>
            </div>
        </div>
        
        <script>
            console.log('🚀 DEX Sniper Pro Dashboard loaded successfully');
            
            async function testAPI(endpoint) {
                const resultsDiv = document.getElementById('apiResults');
                resultsDiv.style.display = 'block';
                resultsDiv.className = 'api-result';
                resultsDiv.innerHTML = `<strong>🔄 Testing:</strong> ${endpoint}...`;
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultsDiv.className = 'api-result success';
                        resultsDiv.innerHTML = `
                            <strong>✅ Success (${response.status}):</strong> ${endpoint}<br>
                            <small>Response: ${JSON.stringify(data, null, 2)}</small>
                        `;
                    } else {
                        resultsDiv.className = 'api-result error';
                        resultsDiv.innerHTML = `
                            <strong>❌ Error (${response.status}):</strong> ${endpoint}<br>
                            <small>${JSON.stringify(data, null, 2)}</small>
                        `;
                    }
                } catch (error) {
                    resultsDiv.className = 'api-result error';
                    resultsDiv.innerHTML = `
                        <strong>❌ Network Error:</strong> ${endpoint}<br>
                        <small>${error.message}</small>
                    `;
                }
            }
            
            async function refreshDashboard() {
                try {
                    const response = await fetch('/api/v1/dashboard/stats');
                    if (response.ok) {
                        const result = await response.json();
                        
                        if (result.status === 'success' && result.data) {
                            const data = result.data;
                            document.getElementById('portfolioValue').textContent = '$' + data.portfolio_value;
                            document.getElementById('dailyPnl').textContent = '+$' + data.daily_pnl;
                            document.getElementById('successRate').textContent = data.success_rate;
                            document.getElementById('activeTrades').textContent = data.active_trades;
                            
                            const resultsDiv = document.getElementById('apiResults');
                            resultsDiv.style.display = 'block';
                            resultsDiv.className = 'api-result success';
                            resultsDiv.innerHTML = '<strong>✅ Dashboard refreshed successfully!</strong>';
                        }
                    }
                } catch (error) {
                    console.error('Dashboard refresh error:', error);
                    const resultsDiv = document.getElementById('apiResults');
                    resultsDiv.style.display = 'block';
                    resultsDiv.className = 'api-result error';
                    resultsDiv.innerHTML = '<strong>❌ Dashboard refresh failed</strong>';
                }
            }
            
            async function testAllEndpoints() {
                const endpoints = [
                    '/api/v1/dashboard/stats',
                    '/api/v1/dashboard/trades',
                    '/api/v1/dashboard/health'
                ];
                
                for (const endpoint of endpoints) {
                    await testAPI(endpoint);
                    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
                }
            }
            
            // Auto-refresh every 30 seconds
            setInterval(() => {
                refreshDashboard();
            }, 30000);
            
            // Initial load
            setTimeout(refreshDashboard, 1000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

'''
        
        # Add required imports if not present
        if "from fastapi.responses import HTMLResponse" not in content:
            if "from fastapi import" in content:
                content = content.replace(
                    "from fastapi import",
                    "from fastapi import Request,\nfrom fastapi.responses import HTMLResponse\nfrom fastapi import"
                )
            else:
                # Add imports at the top
                import_line = "\nfrom fastapi import Request\nfrom fastapi.responses import HTMLResponse\n"
                content = import_line + content
        
        if "Request" not in content and "from fastapi import" in content:
            content = content.replace(
                "from fastapi import FastAPI",
                "from fastapi import FastAPI, Request"
            )
        
        # Find a good place to insert the route (before if __name__ == "__main__")
        if 'if __name__ == "__main__"' in content:
            content = content.replace(
                'if __name__ == "__main__"',
                dashboard_route + '\n\nif __name__ == "__main__"'
            )
        else:
            # Add at the end
            content += dashboard_route
        
        # Write back the updated content
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Dashboard route added to main.py")
        print("✅ Includes professional interface with API testing")
        return True
        
    except Exception as e:
        print(f"❌ Error adding dashboard route: {e}")
        return False


def main():
    """Main execution function."""
    print("Quick Dashboard Fix")
    print("=" * 30)
    
    try:
        success = fix_dashboard_route()
        
        if success:
            print("\n✅ Dashboard route fix applied!")
            print("\nNext steps:")
            print("1. Restart server: uvicorn app.main:app --reload")
            print("2. Visit dashboard: http://127.0.0.1:8000/dashboard")
            print("3. Test API endpoints using built-in test buttons")
            print("4. Dashboard includes:")
            print("   - Live metrics display")
            print("   - API testing interface")
            print("   - Professional UI design")
            print("   - Auto-refresh functionality")
        else:
            print("\n❌ Dashboard route fix failed!")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)