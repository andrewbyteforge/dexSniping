"""
Restore Original Dashboard Template
File: restore_original_dashboard.py

Restores the original professional dashboard template with sidebar layout
and fixes the template serving functionality.
"""

import os
from pathlib import Path


class DashboardRestorer:
    """Restore the original professional dashboard template."""
    
    def __init__(self):
        self.fixes_applied = 0
        self.errors = []
    
    def create_template_directories(self) -> bool:
        """Create the proper template directory structure."""
        try:
            print("[FIX] Creating template directory structure...")
            
            dirs = [
                "frontend/templates",
                "frontend/templates/pages",
                "frontend/templates/base",
                "frontend/static",
                "frontend/static/css",
                "frontend/static/js"
            ]
            
            for dir_path in dirs:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            
            print("[OK] Template directories created")
            return True
            
        except Exception as e:
            self.errors.append(f"Directory creation failed: {e}")
            return False
    
    def restore_dashboard_template(self) -> bool:
        """Restore the original professional dashboard template."""
        try:
            print("[FIX] Restoring original dashboard template...")
            
            dashboard_file = Path("frontend/templates/pages/dashboard.html")
            
            dashboard_content = '''{% extends "base/layout.html" %}

{% block title %}Dashboard{% endblock %}
{% block page_title %}Trading Dashboard{% endblock %}
{% block page_subtitle %}Real-time portfolio monitoring and trade execution{% endblock %}

{% block extra_css %}
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        transition: transform 0.2s ease-in-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .opportunity-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        transition: box-shadow 0.2s ease-in-out;
    }
    
    .opportunity-card:hover {
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
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
    
    .liquidity-badge {
        background: linear-gradient(45deg, #06b6d4, #3b82f6);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .trading-controls {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .btn-trade {
        background: linear-gradient(45deg, #10b981, #059669);
        color: white;
        border: none;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
    
    .btn-trade:hover {
        background: linear-gradient(45deg, #059669, #047857);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
    }
    
    .activity-feed {
        max-height: 400px;
        overflow-y: auto;
    }
    
    .activity-item {
        border-left: 3px solid #e2e8f0;
        padding-left: 1rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease-in-out;
    }
    
    .activity-item:hover {
        border-left-color: #667eea;
    }
    
    .chart-container {
        position: relative;
        height: 300px;
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
    }
</style>
{% endblock %}

{% block content %}
<!-- Dashboard Stats Row -->
<div class="row g-4 mb-4">
    <!-- Portfolio Value -->
    <div class="col-xl-3 col-md-6">
        <div class="card metric-card h-100">
            <div class="card-body text-center">
                <div class="metric-value" id="portfolioValue">$1,247.83</div>
                <div class="metric-label">Portfolio Value</div>
                <small class="d-block mt-2">
                    <i class="bi bi-trending-up"></i>
                    +2.4% today
                </small>
            </div>
        </div>
    </div>
    
    <!-- Daily P&L -->
    <div class="col-xl-3 col-md-6">
        <div class="card metric-card h-100">
            <div class="card-body text-center">
                <div class="metric-value" id="dailyPnl">+$45.67</div>
                <div class="metric-label">Daily P&L</div>
                <small class="d-block mt-2">
                    <i class="bi bi-graph-up"></i>
                    78.5% win rate
                </small>
            </div>
        </div>
    </div>
    
    <!-- Active Positions -->
    <div class="col-xl-3 col-md-6">
        <div class="card metric-card h-100">
            <div class="card-body text-center">
                <div class="metric-value" id="activePositions">3</div>
                <div class="metric-label">Active Positions</div>
                <small class="d-block mt-2">
                    <i class="bi bi-lightning"></i>
                    Auto-trading on
                </small>
            </div>
        </div>
    </div>
    
    <!-- Success Rate -->
    <div class="col-xl-3 col-md-6">
        <div class="card metric-card h-100">
            <div class="card-body text-center">
                <div class="metric-value" id="successRate">78.5%</div>
                <div class="metric-label">Success Rate</div>
                <small class="d-block mt-2">
                    <i class="bi bi-target"></i>
                    127 trades total
                </small>
            </div>
        </div>
    </div>
</div>

<!-- Main Dashboard Content -->
<div class="row g-4">
    <!-- Live Opportunities -->
    <div class="col-xl-8">
        <div class="card h-100">
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
                    <!-- Opportunity items will be loaded here -->
                    <div class="opportunity-card p-3 mb-3">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <div class="token-symbol">PEPE</div>
                                <small class="text-muted">PepeCoin</small>
                            </div>
                            <div class="col-md-2">
                                <div class="fw-bold">$0.00000123</div>
                                <div class="price-change-positive">+156.7%</div>
                            </div>
                            <div class="col-md-2">
                                <span class="liquidity-badge">$47.2K</span>
                            </div>
                            <div class="col-md-2">
                                <small class="text-muted">Age:</small>
                                <div class="fw-bold">2h 14m</div>
                            </div>
                            <div class="col-md-3 text-end">
                                <button class="btn btn-trade btn-sm me-2">
                                    <i class="bi bi-lightning"></i>
                                    Snipe
                                </button>
                                <button class="btn btn-outline-secondary btn-sm">
                                    <i class="bi bi-info-circle"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="opportunity-card p-3 mb-3">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <div class="token-symbol">WOJAK</div>
                                <small class="text-muted">Wojak Coin</small>
                            </div>
                            <div class="col-md-2">
                                <div class="fw-bold">$0.000087</div>
                                <div class="price-change-positive">+89.4%</div>
                            </div>
                            <div class="col-md-2">
                                <span class="liquidity-badge">$23.1K</span>
                            </div>
                            <div class="col-md-2">
                                <small class="text-muted">Age:</small>
                                <div class="fw-bold">4h 32m</div>
                            </div>
                            <div class="col-md-3 text-end">
                                <button class="btn btn-trade btn-sm me-2">
                                    <i class="bi bi-lightning"></i>
                                    Snipe
                                </button>
                                <button class="btn btn-outline-secondary btn-sm">
                                    <i class="bi bi-info-circle"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="text-center">
                    <button class="btn btn-outline-primary" onclick="loadMoreOpportunities()">
                        <i class="bi bi-plus-circle"></i>
                        Load More Opportunities
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Trading Controls & Activity -->
    <div class="col-xl-4">
        <!-- Trading Controls -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-sliders text-primary"></i>
                    Trading Controls
                </h5>
            </div>
            <div class="card-body">
                <div class="trading-controls">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Auto Trading</label>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="autoTrading" checked>
                            <label class="form-check-label" for="autoTrading">
                                Enabled
                            </label>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label fw-bold">Max Position Size</label>
                        <div class="input-group">
                            <input type="number" class="form-control" value="0.1" step="0.01">
                            <span class="input-group-text">ETH</span>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label fw-bold">Risk Level</label>
                        <select class="form-select">
                            <option value="conservative">Conservative</option>
                            <option value="moderate" selected>Moderate</option>
                            <option value="aggressive">Aggressive</option>
                        </select>
                    </div>
                    
                    <button class="btn btn-trade w-100">
                        <i class="bi bi-gear"></i>
                        Update Settings
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-clock-history text-primary"></i>
                    Recent Activity
                </h5>
            </div>
            <div class="card-body">
                <div class="activity-feed">
                    <div class="activity-item">
                        <div class="d-flex justify-content-between">
                            <strong>PEPE Buy</strong>
                            <span class="text-success">+$23.40</span>
                        </div>
                        <small class="text-muted">2 minutes ago</small>
                    </div>
                    
                    <div class="activity-item">
                        <div class="d-flex justify-content-between">
                            <strong>WOJAK Sell</strong>
                            <span class="text-success">+$15.67</span>
                        </div>
                        <small class="text-muted">15 minutes ago</small>
                    </div>
                    
                    <div class="activity-item">
                        <div class="d-flex justify-content-between">
                            <strong>SHIB Buy</strong>
                            <span class="text-danger">-$8.21</span>
                        </div>
                        <small class="text-muted">1 hour ago</small>
                    </div>
                </div>
                
                <div class="text-center mt-3">
                    <a href="/activity" class="btn btn-outline-primary btn-sm">
                        <i class="bi bi-list"></i>
                        View All Activity
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Performance Chart Row -->
<div class="row g-4 mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-graph-up text-primary"></i>
                    Portfolio Performance
                </h5>
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    console.log('🚀 DEX Sniper Pro Dashboard loaded successfully');
    
    // Dashboard functionality
    async function refreshOpportunities() {
        console.log('🔄 Refreshing opportunities...');
        try {
            const response = await fetch('/api/v1/tokens/discover?limit=10');
            const data = await response.json();
            console.log('✅ Opportunities refreshed:', data);
            
            // Update the UI
            updateOpportunitiesDisplay(data);
        } catch (error) {
            console.error('❌ Failed to refresh opportunities:', error);
        }
    }
    
    async function loadDashboardData() {
        try {
            const response = await fetch('/api/v1/dashboard/stats');
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                const data = result.data;
                document.getElementById('portfolioValue').textContent = '$' + data.portfolio_value;
                document.getElementById('dailyPnl').textContent = '+$' + data.daily_pnl;
                document.getElementById('successRate').textContent = data.success_rate;
                document.getElementById('activePositions').textContent = data.active_trades;
                
                console.log('✅ Dashboard data updated');
            }
        } catch (error) {
            console.error('❌ Dashboard data load failed:', error);
        }
    }
    
    function updateOpportunitiesDisplay(data) {
        // Implementation for updating opportunities display
        console.log('📊 Updating opportunities display');
    }
    
    function loadMoreOpportunities() {
        console.log('📈 Loading more opportunities...');
        refreshOpportunities();
    }
    
    // Initialize Chart.js performance chart
    function initPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'now'],
                    datasets: [{
                        label: 'Portfolio Value',
                        data: [1200, 1215, 1198, 1230, 1245, 1242, 1248],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Auto-refresh dashboard every 30 seconds
    setInterval(loadDashboardData, 30000);
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        loadDashboardData();
        initPerformanceChart();
        
        // Test API connectivity
        setTimeout(() => {
            refreshOpportunities();
        }, 1000);
    });
</script>
{% endblock %}'''
            
            dashboard_file.write_text(dashboard_content, encoding='utf-8')
            print("[OK] Dashboard template restored")
            return True
            
        except Exception as e:
            self.errors.append(f"Dashboard template restoration failed: {e}")
            return False
    
    def restore_base_layout(self) -> bool:
        """Restore the base layout template with sidebar."""
        try:
            print("[FIX] Restoring base layout template...")
            
            layout_file = Path("frontend/templates/base/layout.html")
            layout_file.parent.mkdir(parents=True, exist_ok=True)
            
            layout_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}DEX Sniper Pro{% endblock %} - Professional Trading Dashboard</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
    
    {% block extra_css %}{% endblock %}
    
    <style>
        :root {
            --sidebar-width: 280px;
            --sidebar-collapsed-width: 70px;
            --header-height: 70px;
            --primary-color: #667eea;
            --secondary-color: #764ba2;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: #f8fafc;
            margin: 0;
            padding: 0;
        }
        
        /* Sidebar Styles */
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            width: var(--sidebar-width);
            height: 100vh;
            background: linear-gradient(180deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            z-index: 1000;
            overflow-y: auto;
            transition: all 0.3s ease;
        }
        
        .sidebar-brand {
            padding: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }
        
        .sidebar-nav {
            padding: 1rem 0;
        }
        
        .sidebar .nav-link {
            color: rgba(255, 255, 255, 0.8);
            padding: 0.75rem 1.5rem;
            border: none;
            display: flex;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .sidebar .nav-link:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        
        .sidebar .nav-link.active {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border-right: 3px solid #fbbf24;
        }
        
        .sidebar .nav-link i {
            width: 20px;
            margin-right: 0.75rem;
        }
        
        /* Main Content */
        .main-content {
            margin-left: var(--sidebar-width);
            min-height: 100vh;
            transition: margin-left 0.3s ease;
        }
        
        .top-nav {
            background: white;
            padding: 1rem 2rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .content-area {
            padding: 2rem;
        }
        
        /* Live Indicator */
        .live-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.375rem 0.75rem;
            background: rgba(25, 135, 84, 0.1);
            border: 1px solid rgba(25, 135, 84, 0.3);
            border-radius: 8px;
            color: #198754;
            font-size: 0.875rem;
        }
        
        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: #198754;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            
            .sidebar.show {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <!-- Sidebar Navigation -->
    {% include 'base/sidebar.html' %}

    <!-- Main Content Area -->
    <div class="main-content">
        <!-- Top Navigation Bar -->
        <div class="top-nav">
            <button class="btn btn-link d-md-none me-3" id="sidebarToggle">
                <i class="bi bi-list fs-4"></i>
            </button>
            
            <div class="me-auto">
                <h5 class="mb-0">{% block page_title %}Professional Trading Dashboard{% endblock %}</h5>
                <small class="text-muted">{% block page_subtitle %}Real-time DEX monitoring and trading{% endblock %}</small>
            </div>
            
            <div class="d-flex align-items-center gap-3">
                <div class="live-indicator">
                    <span class="pulse-dot"></span>
                    <span id="connection-status">Live</span>
                </div>
                <div class="dropdown">
                    <button class="btn btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <i class="bi bi-person-circle"></i>
                        Account
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#"><i class="bi bi-person"></i> Profile</a></li>
                        <li><a class="dropdown-item" href="#"><i class="bi bi-gear"></i> Settings</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#"><i class="bi bi-box-arrow-right"></i> Logout</a></li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Page Content -->
        <div class="content-area">
            {% block content %}
            <!-- Page-specific content will be inserted here -->
            {% endblock %}
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Sidebar Toggle Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const sidebar = document.getElementById('sidebar');
            const sidebarToggle = document.getElementById('sidebarToggle');
            
            if (sidebarToggle) {
                sidebarToggle.addEventListener('click', function() {
                    sidebar.classList.toggle('show');
                });
            }
        });
    </script>
    
    <!-- Page-specific JavaScript -->
    {% block extra_js %}{% endblock %}
</body>
</html>'''
            
            layout_file.write_text(layout_content, encoding='utf-8')
            print("[OK] Base layout template restored")
            return True
            
        except Exception as e:
            self.errors.append(f"Base layout restoration failed: {e}")
            return False
    
    def restore_sidebar_template(self) -> bool:
        """Restore the sidebar navigation template."""
        try:
            print("[FIX] Restoring sidebar template...")
            
            sidebar_file = Path("frontend/templates/base/sidebar.html")
            
            sidebar_content = '''<!-- DEX Sniper Pro - Sidebar Navigation Component -->
<nav class="sidebar" id="sidebar">
    <!-- Brand Section -->
    <div class="sidebar-brand">
        <div class="d-flex align-items-center justify-content-center">
            <div class="brand-icon me-2">
                <i class="bi bi-lightning-charge-fill text-warning fs-3"></i>
            </div>
            <div class="brand-text">
                <h5 class="mb-0 fw-bold">DEX Sniper</h5>
                <small class="text-light opacity-75">Pro v5.0</small>
            </div>
        </div>
    </div>

    <!-- Navigation Menu -->
    <div class="sidebar-nav">
        <ul class="nav flex-column">
            <!-- Dashboard -->
            <li class="nav-item">
                <a class="nav-link active" href="/dashboard">
                    <i class="bi bi-speedometer2"></i>
                    <span class="nav-text">Dashboard</span>
                    <span class="live-indicator ms-auto">
                        <span class="pulse-dot"></span>
                    </span>
                </a>
            </li>

            <!-- Token Discovery -->
            <li class="nav-item">
                <a class="nav-link" href="/token-discovery">
                    <i class="bi bi-search"></i>
                    <span class="nav-text">Token Discovery</span>
                    <span class="badge bg-success ms-auto" id="new-tokens-count">Live</span>
                </a>
            </li>

            <!-- Live Trading -->
            <li class="nav-item">
                <a class="nav-link" href="/trading">
                    <i class="bi bi-graph-up-arrow"></i>
                    <span class="nav-text">Live Trading</span>
                    <span class="badge bg-warning ms-auto">AI</span>
                </a>
            </li>

            <!-- Portfolio -->
            <li class="nav-item">
                <a class="nav-link" href="/portfolio">
                    <i class="bi bi-pie-chart"></i>
                    <span class="nav-text">Portfolio</span>
                    <span class="badge bg-info ms-auto">3</span>
                </a>
            </li>

            <!-- Wallet Connection -->
            <li class="nav-item">
                <a class="nav-link" href="/wallet">
                    <i class="bi bi-wallet2"></i>
                    <span class="nav-text">Wallet</span>
                    <span class="badge bg-secondary ms-auto">Connect</span>
                </a>
            </li>

            <li class="nav-item">
                <hr class="text-light opacity-25">
            </li>

            <!-- Settings -->
            <li class="nav-item">
                <a class="nav-link" href="/settings">
                    <i class="bi bi-gear"></i>
                    <span class="nav-text">Settings</span>
                </a>
            </li>

            <!-- API Documentation -->
            <li class="nav-item">
                <a class="nav-link" href="/api/docs" target="_blank">
                    <i class="bi bi-book"></i>
                    <span class="nav-text">API Docs</span>
                    <i class="bi bi-box-arrow-up-right ms-auto"></i>
                </a>
            </li>

            <!-- Health Status -->
            <li class="nav-item">
                <a class="nav-link" href="/health">
                    <i class="bi bi-heart-pulse"></i>
                    <span class="nav-text">Health Status</span>
                    <span class="badge bg-success ms-auto">OK</span>
                </a>
            </li>
        </ul>
    </div>

    <!-- Sidebar Footer -->
    <div class="sidebar-footer p-3 mt-auto">
        <!-- Connection Status Widget -->
        <div class="connection-widget p-2 rounded mb-2" style="background: rgba(255, 255, 255, 0.1);">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <small class="text-light opacity-75">Status</small>
                    <div class="fw-bold">
                        <i class="bi bi-dot text-success"></i>
                        <span id="sidebar-status">Operational</span>
                    </div>
                </div>
                <div class="text-end">
                    <small class="text-light opacity-75">Success</small>
                    <div class="fw-bold">93.8%</div>
                </div>
            </div>
        </div>

        <!-- Quick Stats -->
        <div class="quick-stats p-2 rounded" style="background: rgba(255, 255, 255, 0.1);">
            <div class="row g-1 text-center">
                <div class="col-4">
                    <small class="text-light opacity-75">Tokens</small>
                    <div class="fw-bold">47</div>
                </div>
                <div class="col-4">
                    <small class="text-light opacity-75">Active</small>
                    <div class="fw-bold">3</div>
                </div>
                <div class="col-4">
                    <small class="text-light opacity-75">P&L</small>
                    <div class="fw-bold text-warning">+78.5%</div>
                </div>
            </div>
        </div>
    </div>
</nav>

<!-- Mobile Sidebar Overlay -->
<div class="sidebar-overlay" id="sidebar-overlay"></div>'''
            
            sidebar_file.write_text(sidebar_content, encoding='utf-8')
            print("[OK] Sidebar template restored")
            return True
            
        except Exception as e:
            self.errors.append(f"Sidebar template restoration failed: {e}")
            return False
    
    def fix_main_app_template_routing(self) -> bool:
        """Fix the main app to properly serve templates."""
        try:
            print("[FIX] Fixing main app template routing...")
            
            main_file = Path("app/main.py")
            
            if not main_file.exists():
                print("[ERROR] app/main.py not found!")
                return False
            
            # Read current content
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ensure proper imports
            required_imports = [
                "from fastapi import FastAPI, Request",
                "from fastapi.templating import Jinja2Templates",
                "from fastapi.responses import HTMLResponse",
                "from fastapi.staticfiles import StaticFiles"
            ]
            
            for import_line in required_imports:
                if import_line not in content:
                    # Add missing imports
                    if "from fastapi import" in content:
                        content = content.replace(
                            "from fastapi import FastAPI",
                            "from fastapi import FastAPI, Request\nfrom fastapi.templating import Jinja2Templates\nfrom fastapi.responses import HTMLResponse\nfrom fastapi.staticfiles import StaticFiles"
                        )
                        break
            
            # Add template configuration if not present
            if "Jinja2Templates" not in content:
                template_config = '\n# Template configuration\ntemplates = Jinja2Templates(directory="frontend/templates")\n'
                # Insert after imports
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('app = FastAPI'):
                        lines.insert(i, template_config)
                        break
                content = '\n'.join(lines)
            
            # Ensure dashboard route exists
            if '@app.get("/dashboard"' not in content:
                dashboard_route = '''
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the professional dashboard with sidebar layout."""
    try:
        return templates.TemplateResponse(
            "pages/dashboard.html", 
            {"request": request}
        )
    except Exception as e:
        print(f"Template error: {e}")
        # Fallback response
        return HTMLResponse(content="""
        <h1>DEX Sniper Pro Dashboard</h1>
        <p>Dashboard is loading... Please refresh the page.</p>
        <p><a href="/api/v1/dashboard/stats">Test API</a></p>
        """)

'''
                # Add before if __name__ == "__main__"
                if 'if __name__ == "__main__"' in content:
                    content = content.replace(
                        'if __name__ == "__main__"',
                        dashboard_route + '\nif __name__ == "__main__"'
                    )
                else:
                    content += dashboard_route
            
            # Write back the updated content
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[OK] Main app template routing fixed")
            return True
            
        except Exception as e:
            self.errors.append(f"Main app template routing fix failed: {e}")
            return False
    
    def apply_all_fixes(self) -> dict:
        """Apply all dashboard restoration fixes."""
        print("Restore Original Dashboard Template")
        print("=" * 50)
        
        fixes = {
            "create_directories": self.create_template_directories(),
            "restore_dashboard": self.restore_dashboard_template(),
            "restore_layout": self.restore_base_layout(),
            "restore_sidebar": self.restore_sidebar_template(),
            "fix_routing": self.fix_main_app_template_routing()
        }
        
        self.fixes_applied = sum(fixes.values())
        
        print(f"\nDashboard Restoration Results:")
        for fix_name, success in fixes.items():
            status = "[OK]" if success else "[ERROR]"
            print(f"  {status} {fix_name.replace('_', ' ').title()}")
        
        print(f"\nFixes applied: {self.fixes_applied}/5")
        
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        
        return fixes


def main():
    """Main execution function."""
    try:
        restorer = DashboardRestorer()
        results = restorer.apply_all_fixes()
        
        all_success = all(results.values())
        
        if all_success:
            print("\n[SUCCESS] Original dashboard template restored!")
            print("\nRestored Components:")
            print("  - Professional sidebar navigation")
            print("  - Live trading dashboard with metrics")
            print("  - Responsive layout with modern design")
            print("  - API integration and testing")
            print("  - Performance charts and analytics")
            print("\nNext steps:")
            print("1. Restart server: uvicorn app.main:app --reload")
            print("2. Visit dashboard: http://127.0.0.1:8000/dashboard")
            print("3. Enjoy your professional trading interface!")
        else:
            print("\n[PARTIAL] Some template restoration failed!")
            print("Check error messages above")
        
        return all_success
        
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)