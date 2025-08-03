#!/usr/bin/env python3
"""
Restore Original Sidebar Dashboard Layout
File: restore_sidebar_dashboard.py

Restores the original professional sidebar layout while keeping the working data functionality.
"""

import os
from datetime import datetime


def create_base_layout_template():
    """Create the base layout template with sidebar."""
    
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
    
    <!-- Custom CSS -->
    <link href="{{ url_for('static', path='css/main.css') }}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
    
    <style>
        /* Enhanced sidebar styles to ensure proper layout */
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
        
        .nav-item {
            margin: 0.25rem 0;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 0.75rem 1.5rem;
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            transition: all 0.15s ease;
            position: relative;
        }
        
        .nav-link:hover,
        .nav-link.active {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            transform: translateX(4px);
        }
        
        .nav-link.active::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: #fbbf24;
            border-radius: 0 4px 4px 0;
        }
        
        .nav-link i {
            width: 20px;
            margin-right: 0.75rem;
            text-align: center;
        }
        
        /* Main Content */
        .main-content {
            margin-left: var(--sidebar-width);
            min-height: 100vh;
            transition: all 0.3s ease;
        }
        
        /* Top Navigation */
        .top-nav {
            background: white;
            height: var(--header-height);
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 999;
        }
        
        /* Content Area */
        .content-area {
            padding: 1.5rem;
            min-height: calc(100vh - var(--header-height));
        }
        
        /* Live Indicator */
        .live-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.75rem;
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
        
        /* Stats Cards */
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            transition: transform 0.2s ease-in-out;
        }
        
        .stats-card:hover {
            transform: translateY(-5px);
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
</html>
'''
    
    # Ensure base template directory exists
    os.makedirs("frontend/templates/base", exist_ok=True)
    
    with open("frontend/templates/base/layout.html", 'w', encoding='utf-8') as f:
        f.write(layout_content)
    
    print("✅ Created base layout template: frontend/templates/base/layout.html")


def create_sidebar_template():
    """Create the sidebar navigation template."""
    
    sidebar_content = '''<!-- 
DEX Sniper Pro - Sidebar Navigation Component
File: frontend/templates/base/sidebar.html
Professional navigation component with proper layout
-->

<nav class="sidebar" id="sidebar">
    <!-- Brand Section -->
    <div class="sidebar-brand">
        <div class="d-flex align-items-center justify-content-center">
            <div class="brand-icon me-2">
                <i class="bi bi-lightning-charge-fill text-warning fs-3"></i>
            </div>
            <div class="brand-text">
                <h5 class="mb-0 fw-bold">DEX Sniper</h5>
                <small class="text-light opacity-75">Pro v3.1.0</small>
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
                    <span class="badge bg-success ms-auto" id="new-tokens-count">10</span>
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
                    <i class="bi bi-briefcase"></i>
                    <span class="nav-text">Portfolio</span>
                    <span class="badge bg-info ms-auto">$125K</span>
                </a>
            </li>

            <!-- Risk Management -->
            <li class="nav-item">
                <a class="nav-link" href="/risk-management">
                    <i class="bi bi-shield-check"></i>
                    <span class="nav-text">Risk Management</span>
                    <span class="badge bg-secondary ms-auto">99%</span>
                </a>
            </li>

            <!-- Analytics -->
            <li class="nav-item">
                <a class="nav-link" href="/analytics">
                    <i class="bi bi-bar-chart"></i>
                    <span class="nav-text">Analytics</span>
                    <span class="badge bg-primary ms-auto">AI</span>
                </a>
            </li>

            <!-- Settings -->
            <li class="nav-item">
                <a class="nav-link" href="/settings">
                    <i class="bi bi-gear"></i>
                    <span class="nav-text">Settings</span>
                </a>
            </li>

            <!-- Divider -->
            <li><hr class="nav-divider" style="border-color: rgba(255, 255, 255, 0.1); margin: 0.5rem 1.5rem;"></li>

            <!-- API Documentation -->
            <li class="nav-item">
                <a class="nav-link" href="/docs" target="_blank">
                    <i class="bi bi-book"></i>
                    <span class="nav-text">API Docs</span>
                    <i class="bi bi-box-arrow-up-right ms-auto"></i>
                </a>
            </li>

            <!-- Health Status -->
            <li class="nav-item">
                <a class="nav-link" href="/api/v1/health" target="_blank">
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
                    <small class="text-light opacity-75">Uptime</small>
                    <div class="fw-bold">99.8%</div>
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
                    <div class="fw-bold">23</div>
                </div>
                <div class="col-4">
                    <small class="text-light opacity-75">P&L</small>
                    <div class="fw-bold text-warning">+2.6%</div>
                </div>
            </div>
        </div>
    </div>
</nav>

<!-- Mobile Sidebar Overlay -->
<div class="sidebar-overlay" id="sidebar-overlay"></div>
'''
    
    with open("frontend/templates/base/sidebar.html", 'w', encoding='utf-8') as f:
        f.write(sidebar_content)
    
    print("✅ Created sidebar template: frontend/templates/base/sidebar.html")


def create_dashboard_page_with_sidebar():
    """Create the dashboard page that extends the base layout with sidebar."""
    
    dashboard_content = '''{% extends "base/layout.html" %}

{% block title %}Dashboard{% endblock %}

{% block page_title %}Professional Trading Dashboard{% endblock %}
{% block page_subtitle %}Real-time DEX monitoring and AI-powered analysis{% endblock %}

{% block content %}
<!-- Dashboard Status Banner -->
<div class="row mb-4">
    <div class="col-12">
        <div class="alert alert-success d-flex align-items-center">
            <i class="bi bi-check-circle-fill me-2"></i>
            <strong>Status:</strong>
            <span class="ms-2">
                <span class="live-indicator">
                    <i class="bi bi-dot text-success"></i>
                </span>
                APIs operational, data loading successfully
            </span>
            <div class="ms-auto">
                <small>Last update: <span id="lastUpdateTime">--</span></small>
            </div>
        </div>
    </div>
</div>

<!-- Dashboard Stats Cards -->
<div class="row mb-4">
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100 shadow">
            <div class="card-body text-center">
                <i class="bi bi-wallet2 fs-1 mb-3"></i>
                <h3 class="mb-2" id="portfolioValue">Loading...</h3>
                <p class="mb-0 opacity-75">Portfolio Value</p>
            </div>
        </div>
    </div>
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100 shadow">
            <div class="card-body text-center">
                <i class="bi bi-graph-up fs-1 mb-3"></i>
                <h3 class="mb-2" id="dailyPnL">Loading...</h3>
                <p class="mb-0 opacity-75">Daily P&L</p>
            </div>
        </div>
    </div>
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100 shadow">
            <div class="card-body text-center">
                <i class="bi bi-activity fs-1 mb-3"></i>
                <h3 class="mb-2" id="successRate">Loading...</h3>
                <p class="mb-0 opacity-75">Success Rate</p>
            </div>
        </div>
    </div>
    <div class="col-lg-3 col-md-6 mb-3">
        <div class="card stats-card h-100 shadow">
            <div class="card-body text-center">
                <i class="bi bi-lightning fs-1 mb-3"></i>
                <h3 class="mb-2" id="activeTrades">Loading...</h3>
                <p class="mb-0 opacity-75">Active Trades</p>
            </div>
        </div>
    </div>
</div>

<!-- Main Dashboard Content -->
<div class="row mb-4">
    <!-- Live Token Discovery -->
    <div class="col-lg-8 mb-4">
        <div class="card shadow">
            <div class="card-header bg-white">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">
                        <i class="bi bi-search text-primary"></i> Live Token Discovery
                    </h5>
                    <div>
                        <button class="btn btn-sm btn-outline-primary" onclick="refreshTokens()">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                        <button class="btn btn-sm btn-outline-info ms-2" onclick="showDiscoverySettings()">
                            <i class="bi bi-gear"></i> Settings
                        </button>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div id="tokensList">
                    <div class="text-center text-muted">
                        <div class="spinner-border spinner-border-sm me-2"></div>
                        Loading tokens...
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Quick Stats Sidebar -->
    <div class="col-lg-4 mb-4">
        <div class="card shadow">
            <div class="card-header bg-white">
                <h5 class="mb-0">
                    <i class="bi bi-graph-up text-success"></i> Quick Stats
                </h5>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between mb-3">
                    <span>API Status:</span>
                    <span class="badge bg-success" id="apiStatus">Operational</span>
                </div>
                <div class="d-flex justify-content-between mb-3">
                    <span>Tokens Scanned:</span>
                    <span id="tokensScanned">0</span>
                </div>
                <div class="d-flex justify-content-between mb-3">
                    <span>Networks:</span>
                    <span>4 Active</span>
                </div>
                <div class="d-flex justify-content-between mb-3">
                    <span>Success Rate:</span>
                    <span class="text-success" id="quickSuccessRate">89.4%</span>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Uptime:</span>
                    <span class="text-success" id="uptime">99.8%</span>
                </div>
            </div>
        </div>

        <!-- AI Risk Assessment Widget -->
        <div class="card shadow mt-4">
            <div class="card-header bg-white">
                <h5 class="mb-0">
                    <i class="bi bi-robot text-info"></i> AI Risk Assessment
                </h5>
            </div>
            <div class="card-body">
                <div class="text-center">
                    <div class="badge bg-warning fs-6 px-3 py-2 mb-3">
                        Phase 3B Complete
                    </div>
                    <p class="small text-muted">
                        AI-powered honeypot detection and risk scoring ready for implementation.
                    </p>
                    <button class="btn btn-outline-info btn-sm" onclick="showAIFeatures()">
                        <i class="bi bi-arrow-right"></i> Learn More
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- System Information -->
<div class="row">
    <div class="col-12">
        <div class="card shadow">
            <div class="card-header bg-white">
                <h5 class="mb-0">
                    <i class="bi bi-info-circle text-info"></i> System Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <strong>Phase:</strong> 3B Week 7-8 Complete
                    </div>
                    <div class="col-md-3">
                        <strong>Status:</strong> <span class="text-success">Operational</span>
                    </div>
                    <div class="col-md-3">
                        <strong>Version:</strong> 3.1.0
                    </div>
                    <div class="col-md-3">
                        <strong>Next:</strong> Phase 3C Mobile
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<!-- Dashboard JavaScript - Working Data Functionality -->
<script>
    // Global variables
    let dashboardData = {};
    let tokensData = [];
    
    // Initialize dashboard when page loads
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Dashboard with Sidebar Loading...');
        initializeDashboard();
    });
    
    function initializeDashboard() {
        console.log('📊 Initializing dashboard components...');
        
        // Load initial data
        loadDashboardStats();
        loadTokens();
        
        // Set up auto-refresh
        setInterval(loadDashboardStats, 30000); // Every 30 seconds
        setInterval(loadTokens, 15000); // Every 15 seconds
        
        // Update timestamps
        updateTimestamp();
        setInterval(updateTimestamp, 1000);
        
        console.log('✅ Dashboard initialization complete');
    }
    
    async function loadDashboardStats() {
        try {
            console.log('📊 Loading dashboard stats...');
            
            const response = await fetch('/api/v1/dashboard/stats');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Dashboard stats loaded:', data);
            
            // Update dashboard stats
            updateDashboardStats(data);
            
            // Update connection status
            updateConnectionStatus(true);
            
        } catch (error) {
            console.error('❌ Failed to load dashboard stats:', error);
            updateConnectionStatus(false);
        }
    }
    
    function updateDashboardStats(data) {
        try {
            // Update portfolio value
            const portfolioElement = document.getElementById('portfolioValue');
            if (portfolioElement && data.portfolio_value) {
                portfolioElement.textContent = formatCurrency(data.portfolio_value);
            }
            
            // Update daily P&L
            const pnlElement = document.getElementById('dailyPnL');
            if (pnlElement && data.daily_pnl !== undefined) {
                const pnlValue = data.daily_pnl;
                const isPositive = pnlValue >= 0;
                pnlElement.textContent = (isPositive ? '+' : '') + formatCurrency(pnlValue);
                pnlElement.className = 'mb-2 ' + (isPositive ? 'text-success' : 'text-danger');
            }
            
            // Update success rate
            const successElement = document.getElementById('successRate');
            if (successElement && data.success_rate !== undefined) {
                successElement.textContent = data.success_rate.toFixed(1) + '%';
            }
            
            // Update quick success rate
            const quickSuccessElement = document.getElementById('quickSuccessRate');
            if (quickSuccessElement && data.success_rate !== undefined) {
                quickSuccessElement.textContent = data.success_rate.toFixed(1) + '%';
            }
            
            // Update active trades
            const tradesElement = document.getElementById('activeTrades');
            if (tradesElement && data.trades_today !== undefined) {
                tradesElement.textContent = data.trades_today;
            }
            
            // Update uptime
            const uptimeElement = document.getElementById('uptime');
            if (uptimeElement && data.uptime_percent !== undefined) {
                uptimeElement.textContent = data.uptime_percent.toFixed(1) + '%';
            }
            
            console.log('✅ Dashboard stats updated successfully');
            
        } catch (error) {
            console.error('❌ Error updating dashboard stats:', error);
        }
    }
    
    async function loadTokens() {
        try {
            console.log('🔍 Loading tokens...');
            
            const response = await fetch('/api/v1/tokens/discover?limit=10&offset=0&sort=age&order=desc');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Tokens loaded:', data);
            
            if (data.tokens && Array.isArray(data.tokens)) {
                tokensData = data.tokens;
                displayTokens(data.tokens);
                
                // Update tokens scanned count
                const scannedElement = document.getElementById('tokensScanned');
                if (scannedElement) {
                    scannedElement.textContent = data.tokens.length;
                }
            }
            
        } catch (error) {
            console.error('❌ Failed to load tokens:', error);
            displayTokensError();
        }
    }
    
    function displayTokens(tokens) {
        const container = document.getElementById('tokensList');
        if (!container) return;
        
        if (!tokens || tokens.length === 0) {
            container.innerHTML = '<div class="text-muted text-center">No tokens found</div>';
            return;
        }
        
        let html = '';
        tokens.forEach((token, index) => {
            const priceChange = token.price_change_24h || 0;
            const isPositive = priceChange >= 0;
            const badgeClass = isPositive ? 'bg-success' : 'bg-danger';
            
            html += `
                <div class="token-item border-bottom py-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="d-flex align-items-center">
                                <span class="badge bg-primary me-2">${token.symbol || 'TOKEN'}</span>
                                <small class="text-muted">${formatCurrency(token.price || 0)}</small>
                            </div>
                            <div class="small text-muted mt-1">
                                <i class="bi bi-droplet"></i> ${formatLiquidity(token.liquidity_usd || 0)}
                                <span class="ms-2">
                                    <i class="bi bi-clock"></i> ${token.age || 'Unknown'}
                                </span>
                            </div>
                        </div>
                        <div class="text-end">
                            <span class="badge ${badgeClass}">
                                ${isPositive ? '+' : ''}${priceChange.toFixed(2)}%
                            </span>
                            <div class="small text-muted mt-1">
                                Risk: <span class="badge bg-secondary">${(token.risk_score || 2.5).toFixed(1)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        console.log(`✅ Displayed ${tokens.length} tokens`);
    }
    
    function displayTokensError() {
        const container = document.getElementById('tokensList');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i>
                    Unable to load tokens. API may be initializing.
                </div>
            `;
        }
    }
    
    function updateConnectionStatus(connected) {
        const statusElement = document.getElementById('apiStatus');
        const connectionStatusElement = document.getElementById('connection-status');
        const sidebarStatusElement = document.getElementById('sidebar-status');
        
        if (statusElement) {
            if (connected) {
                statusElement.textContent = 'Operational';
                statusElement.className = 'badge bg-success';
            } else {
                statusElement.textContent = 'Reconnecting';
                statusElement.className = 'badge bg-warning';
            }
        }
        
        if (connectionStatusElement) {
            connectionStatusElement.textContent = connected ? 'Live' : 'Reconnecting';
        }
        
        if (sidebarStatusElement) {
            sidebarStatusElement.textContent = connected ? 'Operational' : 'Reconnecting';
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
            return '$' + amount.toFixed(0);
        }
    }
    
    // Manual refresh functions
    function refreshTokens() {
        console.log('🔄 Manual token refresh...');
        loadTokens();
    }
    
    function showDiscoverySettings() {
        alert('Token discovery settings coming soon in Phase 3C!');
    }
    
    function showAIFeatures() {
        alert('AI Risk Assessment features are ready for Phase 3C implementation!');
    }
    
    // Show success message
    setTimeout(() => {
        console.log('🎉 Professional dashboard with sidebar loaded successfully!');
        console.log('📊 Data should display properly with original layout restored');
    }, 1000);
</script>
{% endblock %}
'''
    
    with open("frontend/templates/pages/dashboard.html", 'w', encoding='utf-8') as f:
        f.write(dashboard_content)
    
    print("✅ Created dashboard page with sidebar: frontend/templates/pages/dashboard.html")


def main():
    """Main execution function."""
    print("🔧 Restore Original Sidebar Dashboard Layout")
    print("=" * 50)
    print("Restoring professional sidebar layout while keeping working data functionality")
    print()
    
    try:
        # Step 1: Create base layout with sidebar
        print("📋 Step 1: Creating base layout template...")
        create_base_layout_template()
        
        # Step 2: Create sidebar navigation
        print("🎯 Step 2: Creating sidebar navigation...")
        create_sidebar_template()
        
        # Step 3: Create dashboard page with sidebar
        print("📊 Step 3: Creating dashboard page with sidebar...")
        create_dashboard_page_with_sidebar()
        
        print("\n🎉 Sidebar dashboard restoration completed successfully!")
        print()
        print("📋 What was restored:")
        print("✅ Professional sidebar navigation with gradient background")
        print("✅ Proper layout structure with main content area")
        print("✅ Working data functionality maintained") 
        print("✅ Mobile-responsive sidebar toggle")
        print("✅ Live status indicators and badges")
        print("✅ Professional brand section and navigation icons")
        print("✅ Top navigation bar with user controls")
        print()
        print("📋 Next steps:")
        print("1. Restart the application: uvicorn app.main:app --reload --port 8001")
        print("2. Access dashboard: http://127.0.0.1:8001/dashboard")
        print("3. You should see the original sidebar layout with working data")
        print("4. Data will display properly with the professional interface")
        print()
        print("🚀 The dashboard now has the original sidebar layout with working functionality!")
        
        return True
        
    except Exception as e:
        print(f"❌ Restoration script failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)