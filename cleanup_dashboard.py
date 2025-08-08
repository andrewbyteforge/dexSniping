"""
Cleanup and Fix Dashboard Display Script
File: cleanup_dashboard.py

This script will:
1. Identify unused dashboard files
2. Fix the routing to use the correct sidebar layout
3. Create the proper dashboard template that extends from layout.html
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def identify_dashboard_files():
    """
    Identify all dashboard-related files in the project.
    """
    print("\n🔍 Searching for Dashboard Files...")
    print("=" * 60)
    
    dashboard_files = {
        "active": [],
        "backup": [],
        "orphaned": []
    }
    
    # Check main template locations
    locations = [
        "frontend/templates/pages/dashboard.html",
        "frontend/templates/pages/dashboard.html.backup",
        "frontend/templates/base/layout.html",
        "frontend/templates/base/sidebar.html",
        "frontend/templates/base.html",
        "templates/dashboard.html",
        "dashboard/index.html",
        "frontend/dashboard/index.html"
    ]
    
    for location in locations:
        path = Path(location)
        if path.exists():
            # Check file content to determine if it has sidebar
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    has_sidebar = 'sidebar' in content.lower()
                    extends_layout = 'extends "base/layout.html"' in content
                    
                    file_info = {
                        "path": str(path),
                        "size": path.stat().st_size,
                        "has_sidebar": has_sidebar,
                        "extends_layout": extends_layout
                    }
                    
                    if "backup" in str(path):
                        dashboard_files["backup"].append(file_info)
                    elif extends_layout or str(path) == "frontend/templates/base/layout.html":
                        dashboard_files["active"].append(file_info)
                    else:
                        dashboard_files["orphaned"].append(file_info)
                        
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")
    
    # Display findings
    print("\n📁 Active Files (Using sidebar layout):")
    for file in dashboard_files["active"]:
        print(f"  ✅ {file['path']} - Sidebar: {file['has_sidebar']}")
    
    print("\n📦 Backup Files:")
    for file in dashboard_files["backup"]:
        print(f"  📄 {file['path']} - Size: {file['size']} bytes")
    
    print("\n❓ Orphaned/Unused Files:")
    for file in dashboard_files["orphaned"]:
        print(f"  ⚠️  {file['path']} - Size: {file['size']} bytes")
    
    return dashboard_files


def create_proper_dashboard_with_sidebar():
    """
    Create the correct dashboard.html that extends from layout.html with sidebar.
    """
    print("\n🔧 Creating Proper Dashboard with Sidebar...")
    print("=" * 60)
    
    dashboard_content = '''{% extends "base/layout.html" %}

{% block title %}Trading Dashboard{% endblock %}

{% block page_title %}Professional Trading Dashboard{% endblock %}
{% block page_subtitle %}Real-time DEX monitoring and AI-powered analysis{% endblock %}

{% block content %}
<!-- Dashboard Status Banner -->
<div class="row mb-4">
    <div class="col-12">
        <div class="alert alert-success d-flex align-items-center">
            <i class="bi bi-check-circle-fill me-2"></i>
            <strong>System Status:</strong>
            <span class="ms-2">All systems operational</span>
            <div class="ms-auto">
                <small>Last update: <span id="lastUpdateTime">--:--:--</span></small>
            </div>
        </div>
    </div>
</div>

<!-- Stats Cards Row -->
<div class="row mb-4">
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="text-white-50">Portfolio Value</h6>
                        <h3 class="mb-0" id="portfolioValue">Loading...</h3>
                        <small class="text-white-50">
                            <i class="bi bi-graph-up"></i> 
                            <span id="portfolioChange">+0.00%</span>
                        </small>
                    </div>
                    <i class="bi bi-wallet2 fs-1 text-white-50"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="text-white-50">Daily P&L</h6>
                        <h3 class="mb-0" id="dailyPnL">Loading...</h3>
                        <small class="text-white-50">
                            <span id="dailyPnLPercent">0.00%</span> return
                        </small>
                    </div>
                    <i class="bi bi-graph-up-arrow fs-1 text-white-50"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="text-white-50">Active Trades</h6>
                        <h3 class="mb-0" id="activeTrades">0</h3>
                        <small class="text-white-50">
                            <span id="successRate">0%</span> success
                        </small>
                    </div>
                    <i class="bi bi-activity fs-1 text-white-50"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="text-white-50">Discovered</h6>
                        <h3 class="mb-0" id="tokensDiscovered">0</h3>
                        <small class="text-white-50">
                            <span id="discovered24h">0</span> today
                        </small>
                    </div>
                    <i class="bi bi-search fs-1 text-white-50"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Main Content Area -->
<div class="row">
    <!-- Live Tokens Section -->
    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-lightning-charge text-warning"></i> 
                    Live Token Discovery
                </h5>
            </div>
            <div class="card-body" style="height: 400px; overflow-y: auto;">
                <div id="tokensContainer">
                    <div class="text-center py-5 text-muted">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-3">Scanning for new tokens...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Side Panel -->
    <div class="col-lg-4 mb-4">
        <!-- Performance Chart -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-graph-up text-primary"></i> 
                    Performance
                </h5>
            </div>
            <div class="card-body">
                <canvas id="performanceChart" height="200"></canvas>
            </div>
        </div>
        
        <!-- Recent Alerts -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-bell text-danger"></i> 
                    Alerts
                </h5>
            </div>
            <div class="card-body" style="height: 250px; overflow-y: auto;">
                <div id="alertsContainer">
                    <small class="text-muted">No recent alerts</small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Dashboard initialization
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Dashboard with sidebar initialized');
        initializeDashboard();
    });
    
    async function initializeDashboard() {
        await loadDashboardStats();
        await loadLiveTokens();
        setupAutoRefresh();
    }
    
    async function loadDashboardStats() {
        try {
            const response = await fetch('/api/v1/dashboard/stats');
            const data = await response.json();
            
            // Update stats display
            updateElement('portfolioValue', formatCurrency(data.portfolio_value || 0));
            updateElement('dailyPnL', formatCurrency(data.daily_pnl || 0));
            updateElement('activeTrades', data.trades_today || 0);
            updateElement('tokensDiscovered', data.total_discovered || 0);
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    async function loadLiveTokens() {
        try {
            const response = await fetch('/api/v1/tokens/live');
            const data = await response.json();
            
            if (data.tokens && data.tokens.length > 0) {
                displayTokens(data.tokens);
            }
            
        } catch (error) {
            console.error('Error loading tokens:', error);
        }
    }
    
    function displayTokens(tokens) {
        const container = document.getElementById('tokensContainer');
        let html = '';
        
        tokens.forEach(token => {
            html += `
                <div class="token-card mb-2 p-3 border rounded">
                    <div class="d-flex justify-content-between">
                        <div>
                            <strong>${token.symbol || 'Unknown'}</strong>
                            <br>
                            <small class="text-muted">$${token.price || '0.00'}</small>
                        </div>
                        <div class="text-end">
                            <span class="${token.price_change >= 0 ? 'text-success' : 'text-danger'}">
                                ${token.price_change >= 0 ? '+' : ''}${token.price_change || 0}%
                            </span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html || '<p class="text-muted">No tokens found</p>';
    }
    
    function setupAutoRefresh() {
        setInterval(loadDashboardStats, 30000);
        setInterval(loadLiveTokens, 10000);
        setInterval(updateTimestamp, 1000);
    }
    
    function updateTimestamp() {
        const element = document.getElementById('lastUpdateTime');
        if (element) {
            element.textContent = new Date().toLocaleTimeString();
        }
    }
    
    function updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }
    
    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value || 0);
    }
</script>
{% endblock %}'''
    
    # Create the proper dashboard file
    dashboard_path = Path("frontend/templates/pages/dashboard.html")
    
    # Backup existing if present
    if dashboard_path.exists():
        backup_path = dashboard_path.with_suffix('.html.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
        shutil.copy2(dashboard_path, backup_path)
        print(f"✅ Backed up existing dashboard to: {backup_path}")
    
    # Write new dashboard
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(dashboard_content, encoding='utf-8')
    print(f"✅ Created new dashboard with sidebar at: {dashboard_path}")
    
    return True


def cleanup_orphaned_files():
    """
    Clean up orphaned dashboard files after user confirmation.
    """
    print("\n🧹 Cleanup Orphaned Files")
    print("=" * 60)
    
    orphaned = [
        "dashboard/index.html",
        "frontend/dashboard/index.html",
        "templates/dashboard.html"
    ]
    
    found_orphaned = []
    for file_path in orphaned:
        if Path(file_path).exists():
            found_orphaned.append(file_path)
    
    if not found_orphaned:
        print("✅ No orphaned files found")
        return
    
    print("Found orphaned files:")
    for file in found_orphaned:
        print(f"  - {file}")
    
    response = input("\nDo you want to remove these orphaned files? (yes/no): ").lower()
    
    if response == 'yes':
        for file_path in found_orphaned:
            try:
                Path(file_path).unlink()
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")
    else:
        print("ℹ️  Skipping cleanup")


def main():
    """
    Main cleanup and fix function.
    """
    print("🔧 DEX Sniper Pro - Dashboard Cleanup & Fix")
    print("=" * 60)
    
    # Step 1: Identify all dashboard files
    dashboard_files = identify_dashboard_files()
    
    # Step 2: Create proper dashboard with sidebar
    success = create_proper_dashboard_with_sidebar()
    
    if success:
        print("\n✅ Dashboard fixed successfully!")
        print("\n📝 Next Steps:")
        print("1. Restart your server: uvicorn app.main:app --reload")
        print("2. Navigate to: http://127.0.0.1:8000/dashboard")
        print("3. You should now see your dashboard WITH the sidebar")
        
        # Step 3: Offer to cleanup orphaned files
        cleanup_orphaned_files()
    else:
        print("\n❌ Failed to fix dashboard")
    
    print("\n" + "=" * 60)
    print("✨ Dashboard cleanup complete!")


if __name__ == "__main__":
    main()