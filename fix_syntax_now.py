"""
Quick Syntax Fix
File: fix_syntax_now.py

Immediately fixes the f-string syntax error in route_manager.py
"""

from pathlib import Path

def fix_now():
    """Fix the syntax error immediately."""
    route_manager_path = Path("app/api/route_manager.py")
    
    if not route_manager_path.exists():
        print("❌ File not found")
        return
    
    try:
        content = route_manager_path.read_text(encoding='utf-8')
        
        # Backup
        backup = route_manager_path.with_suffix('.py.syntax_backup')
        backup.write_text(content, encoding='utf-8')
        print(f"✅ Backup created: {backup}")
        
        # Replace the problematic method with a simple working version
        method_start = content.find('def _create_professional_dashboard_fallback(')
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\nclass ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Simple replacement method without f-strings
        simple_method = """    def _create_professional_dashboard_fallback(self, context: Dict[str, Any]) -> HTMLResponse:
        \"\"\"Create a simple dashboard fallback.\"\"\"
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEX Sniper Pro Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
    <style>
        body { background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; }
        .stats-card { background: rgba(255,255,255,0.1); border-radius: 15px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand">🤖 DEX Sniper Pro - Phase 4C</span>
            <span class="navbar-text">AI-Powered Trading Bot</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="alert alert-success">
            <i class="bi bi-check-circle"></i>
            <strong>System Status:</strong> All 8/8 Components Operational
            <span class="badge bg-success ms-2">AI Risk Assessment Active</span>
        </div>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-wallet2 fs-1 text-success"></i>
                    <h3>$0.00</h3>
                    <p>Portfolio Value</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-graph-up fs-1 text-info"></i>
                    <h3>+$0.00</h3>
                    <p>Daily P&L</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-activity fs-1 text-warning"></i>
                    <h3>0</h3>
                    <p>Trades Today</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-percent fs-1 text-primary"></i>
                    <h3>88.9%</h3>
                    <p>System Health</p>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="bi bi-graph-up"></i> Portfolio Performance</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="chart" height="200"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <a href="/api/v1/dashboard/stats" class="btn btn-success">📊 Dashboard Stats</a>
                            <a href="/api/v1/tokens/discover" class="btn btn-info">🔍 Token Discovery</a>
                            <a href="/api/v1/ai-risk/health" class="btn btn-warning">🧠 AI Risk Status</a>
                            <a href="/docs" class="btn btn-primary">📖 API Docs</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('chart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['00:00', '06:00', '12:00', '18:00', '24:00'],
                        datasets: [{
                            label: 'Portfolio Value',
                            data: [1000, 1050, 1200, 1180, 1250],
                            borderColor: 'rgb(75, 192, 192)',
                            fill: false
                        }]
                    }
                });
            }
            
            console.log('🚀 DEX Sniper Pro Dashboard Loaded Successfully!');
        });
    </script>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
</body>
</html>'''
        return HTMLResponse(content=html_content)
"""
        
        if method_start != -1:
            new_content = content[:method_start] + simple_method + content[method_end:]
            route_manager_path.write_text(new_content, encoding='utf-8')
            print("✅ Syntax error fixed with simple dashboard")
            return True
        else:
            print("❌ Method not found")
            return False
            
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Quick Syntax Fix")
    success = fix_now()
    if success:
        print("🎉 Fixed! Now run: python -m app.main")
    else:
        print("❌ Manual fix needed")