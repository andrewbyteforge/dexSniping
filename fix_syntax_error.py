"""
Fix Dashboard Syntax Error
File: fix_syntax_error.py

Replaces the broken JavaScript in dashboard with a clean, working version.
"""

import os
from pathlib import Path

def fix_dashboard_syntax():
    """Fix the syntax error in dashboard JavaScript."""
    
    # Find dashboard file
    dashboard_files = [
        "frontend/templates/pages/dashboard.html",
        "templates/dashboard.html",
        "app/templates/dashboard.html"
    ]
    
    dashboard_path = None
    for file_path in dashboard_files:
        if Path(file_path).exists():
            dashboard_path = Path(file_path)
            break
    
    if not dashboard_path:
        print("❌ Could not find dashboard.html file")
        return False
    
    print(f"✅ Found dashboard at: {dashboard_path}")
    
    try:
        # Read current content
        content = dashboard_path.read_text(encoding='utf-8')
        
        # Create backup
        backup_path = dashboard_path.with_suffix('.html.syntax_backup')
        backup_path.write_text(content, encoding='utf-8')
        print(f"✅ Created backup: {backup_path}")
        
        # Find the {% block extra_js %} section and replace the entire script
        start_marker = "{% block extra_js %}"
        end_marker = "{% endblock %}"
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker, start_pos)
        
        if start_pos == -1 or end_pos == -1:
            print("❌ Could not find JavaScript block markers")
            return False
        
        # Clean JavaScript replacement
        new_js_block = '''{% block extra_js %}
<script>
    // Global variables
    let dashboardData = {};
    let tokensData = [];
    
    // Initialize dashboard when page loads
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Dashboard Loading...');
        initializeDashboard();
    });
    
    function initializeDashboard() {
        console.log('📊 Initializing dashboard...');
        
        loadDashboardStats();
        loadTokens();
        
        setInterval(loadDashboardStats, 30000);
        setInterval(loadTokens, 15000);
        
        updateTimestamp();
        setInterval(updateTimestamp, 1000);
        
        console.log('✅ Dashboard initialization complete');
    }
    
    async function loadDashboardStats() {
        try {
            console.log('📊 Loading dashboard stats...');
            
            const response = await fetch('/api/v1/dashboard/stats');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            console.log('✅ Dashboard stats loaded:', data);
            
            updateDashboardStats(data);
            updateConnectionStatus(true);
            
        } catch (error) {
            console.error('❌ Failed to load dashboard stats:', error);
            updateConnectionStatus(false);
        }
    }
    
    function updateDashboardStats(data) {
        try {
            function safeFormat(value, type) {
                if (value === null || value === undefined) return '0';
                
                if (type === 'currency') {
                    if (typeof value === 'string' && value.includes('$')) return value;
                    return formatCurrency(parseFloat(value) || 0);
                }
                
                if (type === 'percentage') {
                    if (typeof value === 'string' && value.includes('%')) return value;
                    return (parseFloat(value) || 0).toFixed(1) + '%';
                }
                
                return value.toString();
            }
            
            // Update elements safely
            updateElement('portfolioValue', safeFormat(data.portfolio_value, 'currency'));
            updateElement('successRate', safeFormat(data.success_rate, 'percentage'));
            updateElement('quickSuccessRate', safeFormat(data.success_rate, 'percentage'));
            updateElement('activeTrades', data.active_trades || 0);
            
            if (data.daily_pnl !== undefined) {
                const pnlElement = document.getElementById('dailyPnL');
                if (pnlElement) {
                    const pnlValue = parseFloat(data.daily_pnl) || 0;
                    const isPositive = pnlValue >= 0;
                    pnlElement.textContent = (isPositive ? '+' : '') + safeFormat(data.daily_pnl, 'currency');
                    pnlElement.className = 'mb-2 ' + (isPositive ? 'text-success' : 'text-danger');
                }
            }
            
            console.log('✅ Dashboard stats updated successfully');
            
        } catch (error) {
            console.error('❌ Error updating dashboard stats:', error);
        }
    }
    
    function updateElement(id, value) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.textContent = value;
        }
    }
    
    async function loadTokens() {
        try {
            console.log('🔍 Loading tokens...');
            
            const response = await fetch('/api/v1/tokens/discover?limit=10');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            console.log('✅ Tokens API response:', data);
            
            let tokens = [];
            if (data.discovered_tokens && Array.isArray(data.discovered_tokens)) {
                tokens = data.discovered_tokens;
            } else if (data.tokens && Array.isArray(data.tokens)) {
                tokens = data.tokens;
            }
            
            console.log(`📋 Found ${tokens.length} tokens`);
            
            if (tokens.length > 0) {
                tokensData = tokens;
                displayTokens(tokens);
                updateElement('tokensScanned', tokens.length);
            } else {
                displayNoTokens();
            }
            
        } catch (error) {
            console.error('❌ Failed to load tokens:', error);
            displayTokensError();
        }
    }
    
    function displayTokens(tokens) {
        const container = document.getElementById('tokensList');
        if (!container) return;
        
        let html = '';
        tokens.forEach(function(token) {
            const symbol = token.symbol || 'UNKNOWN';
            const price = token.price_usd || token.price || 0;
            const liquidity = token.liquidity_usd || 0;
            const priceChange = token.price_change_24h || 0;
            const riskScore = token.risk_score || 2.5;
            const age = token.age || 'Unknown';
            
            const isPositive = priceChange >= 0;
            const badgeClass = isPositive ? 'bg-success' : 'bg-danger';
            
            html += '<div class="token-item border-bottom py-2">';
            html += '  <div class="d-flex justify-content-between align-items-center">';
            html += '    <div>';
            html += '      <div class="d-flex align-items-center">';
            html += '        <span class="badge bg-primary me-2">' + symbol + '</span>';
            html += '        <small class="text-muted">$' + (price ? price.toFixed(6) : '0.00') + '</small>';
            html += '      </div>';
            html += '      <div class="small text-muted mt-1">';
            html += '        <i class="bi bi-droplet"></i> ' + formatLiquidity(liquidity);
            html += '        <span class="ms-2"><i class="bi bi-clock"></i> ' + age + '</span>';
            html += '      </div>';
            html += '    </div>';
            html += '    <div class="text-end">';
            html += '      <span class="badge ' + badgeClass + '">';
            html += '        ' + (isPositive ? '+' : '') + (priceChange ? priceChange.toFixed(2) : '0.00') + '%';
            html += '      </span>';
            html += '      <div class="small text-muted mt-1">';
            html += '        Risk: <span class="badge bg-secondary">' + (riskScore ? riskScore.toFixed(1) : '0.0') + '</span>';
            html += '      </div>';
            html += '    </div>';
            html += '  </div>';
            html += '</div>';
        });
        
        container.innerHTML = html;
        console.log('✅ Displayed ' + tokens.length + ' tokens');
    }
    
    function displayNoTokens() {
        const container = document.getElementById('tokensList');
        if (container) {
            container.innerHTML = '<div class="text-center text-muted py-4"><i class="bi bi-search fs-2 mb-3"></i><p>No tokens discovered yet</p></div>';
        }
    }
    
    function displayTokensError() {
        const container = document.getElementById('tokensList');
        if (container) {
            container.innerHTML = '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle"></i> Unable to load tokens. <button class="btn btn-sm btn-outline-primary ms-2" onclick="loadTokens()">Retry</button></div>';
        }
    }
    
    function updateConnectionStatus(connected) {
        const statusElement = document.getElementById('apiStatus');
        if (statusElement) {
            statusElement.textContent = connected ? 'Operational' : 'Reconnecting';
            statusElement.className = connected ? 'badge bg-success' : 'badge bg-warning';
        }
    }
    
    function updateTimestamp() {
        const timestampElement = document.getElementById('lastUpdateTime');
        if (timestampElement) {
            timestampElement.textContent = new Date().toLocaleTimeString();
        }
    }
    
    function formatCurrency(amount) {
        if (typeof amount !== 'number') return '$0.00';

        if (amount >= 1000000) {
            return '$' + (amount / 1000000).toFixed(1) + 'M';
        } else if (amount >= 1000) {
            return '$' + (amount / 1000).toFixed(1) + 'K';
        } else {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(amount);
        }
    }

    function formatLiquidity(amount) {
        if (typeof amount !== 'number') return '$0';

        if (amount >= 1000000) {
            return '$' + (amount / 1000000).toFixed(1) + 'M';
        } else if (amount >= 1000) {
            return '$' + (amount / 1000).toFixed(0) + 'K';
        } else {
            return '$' + (amount || 0).toFixed(0);
        }
    }

    function refreshTokens() {
        console.log('🔄 Manual refresh...');
        loadTokens();
    }

    function showDiscoverySettings() {
        alert('Discovery settings coming soon!');
    }

    function showAIFeatures() {
        alert('AI features ready for implementation!');
    }

    console.log('✅ Clean dashboard script loaded');
</script>
{% endblock %}'''

        # Replace the entire JavaScript block
        content = content[:start_pos] + new_js_block + content[end_pos + len(end_marker):]

        # Write the updated content back
        dashboard_path.write_text(content, encoding='utf-8')

        print("✅ Fixed JavaScript syntax errors!")
        print("\nNext steps:")
        print("1. Restart server: uvicorn app.main:app --reload")
        print("2. Refresh dashboard: http://127.0.0.1:8000/dashboard")
        print("3. Check console for: '✅ Clean dashboard script loaded'")

        return True

    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        return False


if __name__ == "__main__":
    print("Fix Dashboard Syntax Error")
    print("=" * 30)
    fix_dashboard_syntax()