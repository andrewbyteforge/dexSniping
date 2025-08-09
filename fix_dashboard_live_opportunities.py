"""
Fix Dashboard Live Opportunities
File: fix_dashboard_live_opportunities.py

Updates the dashboard JavaScript to properly connect to and display 
the enhanced token discovery data in the Live Opportunities section.
"""

import os
from pathlib import Path


def fix_dashboard_opportunities():
    """Fix the dashboard to properly load and display live opportunities."""
    
    print("🔧 Fixing Dashboard Live Opportunities")
    print("=" * 50)
    
    main_file = Path("app/main.py")
    
    if not main_file.exists():
        print("❌ main.py not found!")
        return False
    
    try:
        # Read current content
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the dashboard function and update its JavaScript
        dashboard_start = content.find("# Fallback to embedded dashboard")
        if dashboard_start == -1:
            dashboard_start = content.find("return HTMLResponse(content=\"\"\"")
        
        if dashboard_start == -1:
            print("❌ Could not find dashboard HTML content to update")
            return False
        
        # Find the end of the current dashboard HTML
        html_start = content.find('return HTMLResponse(content="""', dashboard_start)
        html_end = content.find('"""))', html_start) + 4
        
        if html_start == -1 or html_end == -1:
            print("❌ Could not find dashboard HTML boundaries")
            return False
        
        # Create enhanced dashboard HTML with working live opportunities
        enhanced_dashboard_html = '''return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniper Pro Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body { 
                background: #f8fafc; 
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
                color: white;
                z-index: 1000;
                overflow-y: auto;
            }
            .main-content {
                margin-left: 280px;
                padding: 2rem;
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                transition: transform 0.2s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
            }
            .opportunity-card {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                transition: all 0.2s ease;
                background: white;
            }
            .opportunity-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .token-symbol {
                font-weight: 700;
                font-size: 1.1rem;
            }
            .price-change-positive {
                color: #10b981;
                font-weight: 600;
            }
            .price-change-negative {
                color: #ef4444;
                font-weight: 600;
            }
            .risk-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            .risk-low { background: #d1fae5; color: #065f46; }
            .risk-medium { background: #fef3c7; color: #92400e; }
            .risk-high { background: #fee2e2; color: #991b1b; }
            .network-badge {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.7rem;
            }
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="p-4 text-center border-bottom border-light border-opacity-25">
                <h4 class="mb-0">⚡ DEX Sniper</h4>
                <small class="text-light opacity-75">Pro v5.0</small>
            </div>
            <nav class="p-3">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link text-light active" href="/dashboard">
                            <i class="bi bi-speedometer2 me-2"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/activity">
                            <i class="bi bi-clock-history me-2"></i>Activity
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/api/docs">
                            <i class="bi bi-book me-2"></i>API Docs
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/health">
                            <i class="bi bi-heart-pulse me-2"></i>Health
                        </a>
                    </li>
                </ul>
            </nav>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2>Trading Dashboard</h2>
                    <p class="text-muted mb-0">Real-time portfolio monitoring</p>
                </div>
                <div class="badge bg-success">
                    <i class="bi bi-dot"></i> Live
                </div>
            </div>

            <!-- Metrics Row -->
            <div class="row g-4 mb-4">
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="portfolioValue">$1,247.83</div>
                            <div class="opacity-75">Portfolio Value</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value text-success" id="dailyPnl">+$45.67</div>
                            <div class="opacity-75">Daily P&L</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="activePositions">3</div>
                            <div class="opacity-75">Active Positions</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="successRate">78.5%</div>
                            <div class="opacity-75">Success Rate</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Live Opportunities Section -->
            <div class="row g-4 mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">
                                <i class="bi bi-search text-primary"></i>
                                Live Opportunities
                            </h5>
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="refreshOpportunities()">
                                    <i class="bi bi-arrow-clockwise"></i>
                                    Refresh
                                </button>
                                <span class="badge bg-success">
                                    <i class="bi bi-dot"></i>
                                    Live
                                </span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="opportunitiesContainer">
                                <div class="text-center">
                                    <div class="loading-spinner"></div>
                                    <p class="mt-2">Loading opportunities...</p>
                                </div>
                            </div>
                            
                            <div class="text-center mt-3">
                                <button class="btn btn-outline-primary" onclick="loadMoreOpportunities()">
                                    <i class="bi bi-plus-circle"></i>
                                    Load More Opportunities
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- API Testing Section -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">🧪 API Testing Center</h5>
                </div>
                <div class="card-body">
                    <p>Test the API endpoints:</p>
                    <button class="btn btn-primary me-2" onclick="testAPI('/api/v1/dashboard/stats')">
                        <i class="bi bi-graph-up"></i> Dashboard Stats
                    </button>
                    <button class="btn btn-success me-2" onclick="testAPI('/api/v1/tokens/discover')">
                        <i class="bi bi-search"></i> Token Discovery
                    </button>
                    <button class="btn btn-info me-2" onclick="testAPI('/api/v1/tokens/trending')">
                        <i class="bi bi-fire"></i> Trending Tokens
                    </button>
                    <button class="btn btn-warning" onclick="refreshDashboard()">
                        <i class="bi bi-arrow-clockwise"></i> Refresh Data
                    </button>
                    <div id="apiResults" class="mt-3 p-3 bg-light rounded" style="display: none;"></div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Global variables
            let currentTokens = [];
            let isLoading = false;
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                console.log('🚀 DEX Sniper Pro Dashboard loading...');
                refreshDashboard();
                loadOpportunities();
                
                // Auto-refresh every 30 seconds
                setInterval(() => {
                    refreshDashboard();
                    loadOpportunities();
                }, 30000);
            });
            
            async function loadOpportunities() {
                if (isLoading) return;
                
                isLoading = true;
                const container = document.getElementById('opportunitiesContainer');
                
                try {
                    console.log('🔍 Loading live opportunities...');
                    
                    const response = await fetch('/api/v1/tokens/discover?limit=8');
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    console.log('✅ Opportunities loaded:', data);
                    
                    if (data.tokens && data.tokens.length > 0) {
                        currentTokens = data.tokens;
                        displayOpportunities(data.tokens);
                    } else {
                        container.innerHTML = '<p class="text-muted text-center">No opportunities found. Try refreshing.</p>';
                    }
                    
                } catch (error) {
                    console.error('❌ Failed to load opportunities:', error);
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <strong>Unable to load opportunities</strong><br>
                            ${error.message}<br>
                            <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadOpportunities()">
                                Try Again
                            </button>
                        </div>
                    `;
                } finally {
                    isLoading = false;
                }
            }
            
            function displayOpportunities(tokens) {
                const container = document.getElementById('opportunitiesContainer');
                
                if (!tokens || tokens.length === 0) {
                    container.innerHTML = '<p class="text-muted text-center">No opportunities available</p>';
                    return;
                }
                
                const opportunitiesHTML = tokens.map(token => {
                    const changeClass = token.change_24h > 0 ? 'price-change-positive' : 'price-change-negative';
                    const changeIcon = token.change_24h > 0 ? 'bi-trending-up' : 'bi-trending-down';
                    const riskClass = `risk-${token.risk_level}`;
                    
                    return `
                        <div class="opportunity-card">
                            <div class="row align-items-center">
                                <div class="col-md-3">
                                    <div class="d-flex align-items-center">
                                        <div>
                                            <div class="token-symbol">${token.symbol}</div>
                                            <small class="text-muted">${token.name}</small>
                                            <br>
                                            <span class="network-badge">${token.network}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <div class="fw-bold">${token.price}</div>
                                    <div class="${changeClass}">
                                        <i class="bi ${changeIcon}"></i>
                                        ${token.change_24h > 0 ? '+' : ''}${token.change_24h.toFixed(1)}%
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Liquidity:</small>
                                    <div class="fw-bold">$${token.liquidity.toLocaleString()}</div>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Risk:</small>
                                    <div>
                                        <span class="risk-badge ${riskClass}">
                                            ${token.risk_level} (${token.risk_score})
                                        </span>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Age:</small>
                                    <div class="fw-bold">${formatAge(token.age_hours)}</div>
                                </div>
                                <div class="col-md-1 text-end">
                                    <button class="btn btn-primary btn-sm" onclick="snipeToken('${token.symbol}', '${token.address}')">
                                        <i class="bi bi-lightning"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                container.innerHTML = opportunitiesHTML;
                console.log(`✅ Displayed ${tokens.length} opportunities`);
            }
            
            function formatAge(hours) {
                if (hours < 1) return `${Math.round(hours * 60)}m`;
                if (hours < 24) return `${Math.round(hours)}h`;
                return `${Math.round(hours / 24)}d`;
            }
            
            function snipeToken(symbol, address) {
                alert(`Snipe ${symbol} functionality coming soon!\\nAddress: ${address}`);
            }
            
            async function refreshOpportunities() {
                console.log('🔄 Refreshing opportunities...');
                await loadOpportunities();
            }
            
            async function loadMoreOpportunities() {
                console.log('📈 Loading more opportunities...');
                try {
                    const response = await fetch('/api/v1/tokens/discover?limit=15');
                    const data = await response.json();
                    
                    if (data.tokens) {
                        currentTokens = [...currentTokens, ...data.tokens];
                        displayOpportunities(currentTokens.slice(0, 20)); // Show max 20
                    }
                } catch (error) {
                    console.error('❌ Failed to load more opportunities:', error);
                }
            }
            
            async function testAPI(endpoint) {
                const resultsDiv = document.getElementById('apiResults');
                resultsDiv.style.display = 'block';
                resultsDiv.innerHTML = `<strong>🔄 Testing:</strong> ${endpoint}...`;
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultsDiv.className = 'mt-3 p-3 bg-success text-white rounded';
                        resultsDiv.innerHTML = `
                            <strong>✅ Success (${response.status}):</strong> ${endpoint}<br>
                            <small>${JSON.stringify(data, null, 2)}</small>
                        `;
                    } else {
                        resultsDiv.className = 'mt-3 p-3 bg-danger text-white rounded';
                        resultsDiv.innerHTML = `
                            <strong>❌ Error (${response.status}):</strong> ${endpoint}<br>
                            <small>${JSON.stringify(data, null, 2)}</small>
                        `;
                    }
                } catch (error) {
                    resultsDiv.className = 'mt-3 p-3 bg-danger text-white rounded';
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
                            document.getElementById('activePositions').textContent = data.active_trades;
                        }
                    }
                } catch (error) {
                    console.error('❌ Dashboard refresh error:', error);
                }
            }
            
            console.log('✅ DEX Sniper Pro Dashboard loaded successfully!');
        </script>
    </body>
    </html>
    """)'''
        
        # Replace the old HTML with the enhanced version
        new_content = content[:html_start] + enhanced_dashboard_html + content[html_end:]
        
        # Write the updated content
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Dashboard live opportunities fixed successfully!")
        print("\n🎯 What was fixed:")
        print("   - JavaScript now properly calls /api/v1/tokens/discover")
        print("   - Live opportunities display enhanced token data")
        print("   - Professional opportunity cards with full details")
        print("   - Risk assessment with color-coded badges")
        print("   - Network badges for each token")
        print("   - Price change indicators with icons")
        print("   - Auto-refresh every 30 seconds")
        print("   - Error handling and loading states")
        print("   - Snipe buttons for each opportunity")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix dashboard opportunities: {e}")
        return False


def main():
    """Main execution function."""
    try:
        if fix_dashboard_opportunities():
            print("\n" + "=" * 50)
            print("🎉 DASHBOARD LIVE OPPORTUNITIES FIXED!")
            print("=" * 50)
            print("\n✅ Your dashboard now features:")
            print("  - Real-time token discovery integration")
            print("  - Enhanced opportunity cards with full details")
            print("  - Risk assessment and network badges")
            print("  - Auto-refresh every 30 seconds")
            print("  - Professional loading states")
            print("  - Error handling and retry functionality")
            print("\nNext steps:")
            print("1. Restart server: uvicorn app.main:app --reload")
            print("2. Visit dashboard: http://127.0.0.1:8000/dashboard")
            print("3. Watch live opportunities update with real data!")
            print("4. Test the enhanced token discovery system!")
            
            return True
        else:
            print("\n❌ Fix failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)