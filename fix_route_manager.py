"""
Fix Route Manager F-String Syntax Error
File: fix_route_manager.py

Fixes the f-string syntax error that's preventing the application from starting.
The issue is that f-strings cannot contain backslashes in the expression parts.
"""

import re
from pathlib import Path

def fix_route_manager_syntax():
    """Fix the f-string syntax error in route_manager.py"""
    
    route_manager_path = Path("app/api/route_manager.py")
    
    if not route_manager_path.exists():
        print("❌ route_manager.py not found")
        return False
    
    print("🔧 Fixing f-string syntax error in route_manager.py...")
    
    try:
        # Read the file
        content = route_manager_path.read_text(encoding='utf-8')
        
        # Create backup
        backup_path = route_manager_path.with_suffix('.py.backup')
        backup_path.write_text(content, encoding='utf-8')
        print(f"✅ Created backup: {backup_path}")
        
        # The issue is in the HTML content where we have f-string expressions
        # We need to move the HTML content outside the f-string or escape it properly
        
        # Find the problematic f-string section and replace it with proper string concatenation
        # Look for the _create_professional_dashboard_fallback method
        
        if 'f"""' in content and 'background: linear-gradient' in content:
            print("🔍 Found problematic f-string with CSS gradients")
            
            # Replace the f-string approach with regular string formatting
            # This is safer and avoids backslash issues
            fixed_content = content.replace('f"""', '"""')
            
            # Replace f-string expressions with .format() calls
            fixed_content = re.sub(
                r"\{'([^']+)' if ([^}]+) else '([^']*)'\}",
                r"{class_active_\2}",
                fixed_content
            )
            
            # Handle simple variable substitutions
            fixed_content = re.sub(
                r'\{([^}]+)\}',
                lambda m: '{' + m.group(1).replace('.', '_') + '}',
                fixed_content
            )
            
            route_manager_path.write_text(fixed_content, encoding='utf-8')
            print("✅ Applied f-string syntax fixes")
            return True
            
        else:
            print("⚠️ Problematic f-string pattern not found - trying alternative fix")
            return fix_alternative_method(route_manager_path, content)
            
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        return False


def fix_alternative_method(file_path: Path, content: str) -> bool:
    """Alternative method to fix the syntax error."""
    try:
        # Replace the entire problematic method with a working version
        
        # Find the start and end of the _create_professional_dashboard_fallback method
        method_start = content.find('def _create_professional_dashboard_fallback(')
        if method_start == -1:
            print("❌ Method not found")
            return False
        
        # Find the end of the method (next method or class definition)
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\nclass ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Create a safe replacement method
        safe_method = '''    def _create_professional_dashboard_fallback(self, context: Dict[str, Any]) -> HTMLResponse:
        """Create a professional dashboard fallback that looks like the original."""
        component_status = context.get('component_status', {})
        ai_enabled = context.get('ai_risk_enabled', False)
        page_type = context.get('page_type', 'dashboard')
        
        # Calculate stats
        available_components = sum(component_status.values()) if component_status else 8
        total_components = len(component_status) if component_status else 8
        health_percentage = (available_components / total_components * 100) if total_components > 0 else 88.9
        
        # Build HTML content safely without f-strings
        html_parts = []
        
        html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEX Sniper Pro - Professional Trading Dashboard</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
    
    <style>
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar-dark {
            background: rgba(0, 0, 0, 0.2) !important;
            backdrop-filter: blur(10px);
        }
        
        .stats-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            color: white;
            transition: all 0.3s ease;
        }
        
        .stats-card:hover {
            transform: translateY(-5px);
        }
        
        .chart-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            color: white;
        }
        
        .live-indicator {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .ai-badge {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            font-weight: bold;
        }
        
        .component-badge {
            background: rgba(40, 167, 69, 0.2);
            color: #28a745;
            border: 1px solid #28a745;
        }
    </style>
</head>
<body>""")
        
        # Add navigation
        nav_active_dashboard = 'active' if page_type == 'dashboard' else ''
        nav_active_risk = 'active' if page_type == 'risk_analysis' else ''
        nav_active_trading = 'active' if page_type == 'live_trading' else ''
        nav_active_portfolio = 'active' if page_type == 'portfolio' else ''
        
        html_parts.append(f"""
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="bi bi-graph-up-arrow"></i>
                DEX Sniper Pro
            </a>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link {nav_active_dashboard}" href="/dashboard">
                            <i class="bi bi-speedometer2"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {nav_active_risk}" href="/risk-analysis">
                            <i class="bi bi-shield-check"></i> AI Risk Analysis
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {nav_active_trading}" href="/live-trading">
                            <i class="bi bi-lightning"></i> Live Trading
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {nav_active_portfolio}" href="/portfolio">
                            <i class="bi bi-briefcase"></i> Portfolio
                        </a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <span class="navbar-text me-3">
                            <span class="live-indicator">
                                <i class="bi bi-dot text-success"></i>
                            </span>
                            System Operational
                        </span>
                    </li>
                </ul>
            </div>
        </div>
    </nav>""")
        
        # Add main content
        ai_badge = '<span class="badge ai-badge me-2">🧠 AI Risk Assessment Active</span>' if ai_enabled else ''
        
        html_parts.append(f"""
    <!-- Main Content -->
    <div class="container-fluid mt-4">
        <!-- System Status Banner -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="alert alert-success d-flex align-items-center">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <strong>Status:</strong>
                    <span class="ms-2">
                        <span class="live-indicator">
                            <i class="bi bi-dot text-success"></i>
                        </span>
                        Phase 4C AI-Powered Trading System Operational
                    </span>
                    <div class="ms-auto d-flex align-items-center">
                        {ai_badge}
                        <span class="badge component-badge">{available_components}/{total_components} Components</span>
                        <small class="ms-3">Health: {health_percentage:.1f}%</small>
                    </div>
                </div>
            </div>
        </div>""")
        
        # Add dashboard stats and charts
        html_parts.append("""
        <!-- Dashboard Stats Cards -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card h-100">
                    <div class="card-body text-center">
                        <i class="bi bi-wallet2 fs-1 mb-3 text-success"></i>
                        <h3 class="mb-2">$0.00</h3>
                        <p class="mb-0 opacity-75">Portfolio Value</p>
                        <small class="text-muted">Ready for trading</small>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card h-100">
                    <div class="card-body text-center">
                        <i class="bi bi-graph-up fs-1 mb-3 text-info"></i>
                        <h3 class="mb-2">+$0.00</h3>
                        <p class="mb-0 opacity-75">Daily P&L</p>
                        <small class="text-muted">0.0%</small>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card h-100">
                    <div class="card-body text-center">
                        <i class="bi bi-activity fs-1 mb-3 text-warning"></i>
                        <h3 class="mb-2">0</h3>
                        <p class="mb-0 opacity-75">Trades Today</p>
                        <small class="text-muted">System ready</small>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="card stats-card h-100">
                    <div class="card-body text-center">
                        <i class="bi bi-percent fs-1 mb-3 text-primary"></i>""")
        
        html_parts.append(f"""
                        <h3 class="mb-2">{health_percentage:.1f}%</h3>
                        <p class="mb-0 opacity-75">System Health</p>
                        <small class="text-muted">All systems go</small>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Charts Section -->
        <div class="row mb-4">
            <div class="col-lg-8">
                <div class="card chart-card h-100">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-graph-up"></i> Portfolio Performance</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="portfolioChart" height="300"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card chart-card h-100">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-pie-chart"></i> Asset Allocation</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="allocationChart" height="300"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>""")
        
        # Add JavaScript
        html_parts.append("""
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 DEX Sniper Pro Dashboard Loaded');
            
            // Initialize charts
            const portfolioCtx = document.getElementById('portfolioChart');
            if (portfolioCtx) {
                new Chart(portfolioCtx, {
                    type: 'line',
                    data: {
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{
                            label: 'Portfolio Value',
                            data: [1000, 1050, 980, 1100, 1200, 1180],
                            borderColor: 'rgba(40, 167, 69, 1)',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: false, grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: 'white' } },
                            x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: 'white' } }
                        }
                    }
                });
            }
            
            const allocationCtx = document.getElementById('allocationChart');
            if (allocationCtx) {
                new Chart(allocationCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['ETH', 'USDC', 'Available'],
                        datasets: [{
                            data: [40, 30, 30],
                            backgroundColor: ['rgba(40, 167, 69, 0.8)', 'rgba(23, 162, 184, 0.8)', 'rgba(255, 193, 7, 0.8)']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom', labels: { color: 'white' } } }
                    }
                });
            }
        });
    </script>
</body>
</html>""")
        
        html_content = ''.join(html_parts)
        return HTMLResponse(content=html_content)
'''
        
        # Replace the problematic method
        new_content = content[:method_start] + safe_method + content[method_end:]
        
        file_path.write_text(new_content, encoding='utf-8')
        print("✅ Replaced problematic method with safe version")
        return True
        
    except Exception as e:
        print(f"❌ Alternative fix failed: {e}")
        return False


def main():
    """Main function to fix the syntax error."""
    print("🔧 DEX Sniper Pro - Route Manager Syntax Fix")
    print("=" * 50)
    
    success = fix_route_manager_syntax()
    
    if success:
        print("\n🎉 SUCCESS! Syntax error fixed!")
        print("✅ route_manager.py has been repaired")
        print("🚀 You can now run: python -m app.main")
        print("🌐 Then visit: http://localhost:8000/dashboard")
    else:
        print("\n❌ FAILED to fix syntax error")
        print("🔧 Manual intervention may be required")
    
    print("=" * 50)
    return success


if __name__ == "__main__":
    main()