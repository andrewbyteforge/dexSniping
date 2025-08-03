/**
 * Dashboard Live Updates Integration
 * File: frontend/static/js/dashboard-live.js
 * 
 * Real-time dashboard updates for DEX Sniper Pro
 * Connects to backend APIs and provides live data feeds
 */

class DashboardLiveUpdates {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.isConnected = false;
        this.lastUpdate = null;
        this.retryAttempts = 0;
        this.maxRetries = 5;
        
        // Update counters
        this.updateCounters = {
            tokensDiscovered: 0,
            activeTrades: 0,
            arbitrageOps: 0,
            portfolioValue: 125826.86
        };
        
        // Initialize
        this.init();
    }
    
    async init() {
        console.log('🔄 Initializing live dashboard updates...');
        
        // Start live updates
        await this.startLiveUpdates();
        
        // Set up WebSocket connection for real-time data
        this.setupWebSocket();
        
        // Set up auto-refresh
        this.setupAutoRefresh();
        
        console.log('✅ Live updates initialized');
    }
    
    async startLiveUpdates() {
        try {
            // Initial data load
            await this.updateDashboardStats();
            await this.updateTokenDiscovery();
            await this.updateTradingData();
            await this.updateArbitrageData();
            
            this.isConnected = true;
            this.retryAttempts = 0;
            this.updateConnectionStatus(true);
            
        } catch (error) {
            console.error('❌ Failed to start live updates:', error);
            this.handleConnectionError();
        }
    }
    
    async updateDashboardStats() {
        try {
            const response = await fetch('/api/v1/dashboard/stats');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // Update portfolio overview
            this.updatePortfolioOverview(data);
            
            // Update counters
            this.updateCounters.portfolioValue = data.portfolio_value;
            this.updateCounters.activeTrades = data.trades_today;
            
            // Update display
            this.updateStatsDisplay(data);
            
            console.log('📊 Dashboard stats updated');
            
        } catch (error) {
            console.error('Failed to update dashboard stats:', error);
        }
    }
    
    async updateTokenDiscovery() {
        try {
            const response = await fetch('/api/v1/dashboard/tokens/live?limit=10');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // Update tokens discovered counter
            this.updateCounters.tokensDiscovered = data.length;
            
            // Update live token table
            this.updateTokenTable(data);
            
            // Update discovery widgets
            this.updateDiscoveryWidgets(data);
            
            console.log(`🔍 Token discovery updated: ${data.length} tokens`);
            
        } catch (error) {
            console.error('Failed to update token discovery:', error);
            this.showTokenTableError();
        }
    }
    
    async updateTradingData() {
        try {
            const response = await fetch('/api/v1/dashboard/trading/metrics');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // Update trading metrics
            this.updateTradingMetrics(data);
            
            console.log('💹 Trading data updated');
            
        } catch (error) {
            console.error('Failed to update trading data:', error);
        }
    }
    
    async updateArbitrageData() {
        try {
            // Mock arbitrage data - replace with real endpoint when available
            const arbitrageOps = Math.floor(Math.random() * 5) + 1;
            this.updateCounters.arbitrageOps = arbitrageOps;
            
            this.updateArbitrageDisplay(arbitrageOps);
            
        } catch (error) {
            console.error('Failed to update arbitrage data:', error);
        }
    }
    
    updatePortfolioOverview(data) {
        // Update portfolio value
        const portfolioElement = document.querySelector('.summary-stat-value');
        if (portfolioElement) {
            portfolioElement.textContent = this.formatCurrency(data.portfolio_value);
        }
        
        // Update daily P&L
        const pnlElements = document.querySelectorAll('.summary-stat-value');
        if (pnlElements.length > 1) {
            const pnlElement = pnlElements[1];
            const isPositive = data.daily_pnl >= 0;
            pnlElement.textContent = (isPositive ? '+' : '') + this.formatCurrency(data.daily_pnl);
            pnlElement.className = `summary-stat-value ${isPositive ? 'text-success' : 'text-danger'}`;
        }
    }
    
    updateStatsDisplay(data) {
        // Update loading states to actual data
        const widgets = document.querySelectorAll('[data-widget]');
        
        widgets.forEach(widget => {
            const widgetType = widget.dataset.widget;
            const valueElement = widget.querySelector('.widget-value') || 
                                widget.querySelector('.summary-stat-value');
            
            if (!valueElement) return;
            
            switch (widgetType) {
                case 'tokens-discovered':
                    valueElement.textContent = this.updateCounters.tokensDiscovered;
                    this.animateCounterUpdate(valueElement);
                    break;
                    
                case 'active-trades':
                    valueElement.textContent = this.updateCounters.activeTrades;
                    this.animateCounterUpdate(valueElement);
                    break;
                    
                case 'arbitrage-ops':
                    valueElement.textContent = this.updateCounters.arbitrageOps;
                    this.animateCounterUpdate(valueElement);
                    break;
                    
                case 'portfolio-value':
                    valueElement.textContent = this.formatCurrency(data.portfolio_value);
                    this.animateCounterUpdate(valueElement);
                    break;
            }
        });
        
        // Update generic loading text
        this.replaceLoadingText();
    }
    
    updateTokenTable(tokens) {
        const tableBody = document.querySelector('#tokenTableBody') || 
                         document.querySelector('tbody');
        
        if (!tableBody) {
            console.warn('Token table body not found');
            return;
        }
        
        if (tokens.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-3">
                        <i class="bi bi-search"></i>
                        No tokens discovered yet. Scanning...
                    </td>
                </tr>
            `;
            return;
        }
        
        const rows = tokens.map(token => {
            const ageMinutes = Math.floor((Date.now() - new Date(token.last_updated).getTime()) / 60000);
            const riskLevel = this.getRiskLevel(token.risk_score || 5);
            const riskColor = this.getRiskColor(riskLevel);
            
            return `
                <tr class="token-row" data-token="${token.address}">
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="token-icon me-2">
                                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 24px; height: 24px; font-size: 10px;">
                                    ${token.symbol.substring(0, 2)}
                                </div>
                            </div>
                            <div>
                                <div class="fw-semibold">${token.symbol}</div>
                                <div class="small text-muted">${token.name}</div>
                            </div>
                        </div>
                    </td>
                    <td>${token.symbol}</td>
                    <td>
                        <span class="badge bg-secondary">${token.network || 'ETH'}</span>
                    </td>
                    <td>${this.formatCurrency(token.price || 0.001)}</td>
                    <td>${this.formatCurrency(token.market_cap || 0)}</td>
                    <td>${this.formatCurrency(token.liquidity || 0)}</td>
                    <td>
                        <div class="small">${this.formatNumber(token.volume_24h || 0)}</div>
                    </td>
                    <td>
                        <span class="badge bg-info">${ageMinutes}m</span>
                    </td>
                    <td>
                        <span class="badge bg-${riskColor}">${riskLevel}</span>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-sm" onclick="analyzeToken('${token.address}')">
                                <i class="bi bi-search"></i>
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="tradeToken('${token.address}')">
                                <i class="bi bi-currency-exchange"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
        
        tableBody.innerHTML = rows;
        
        // Highlight new tokens
        this.highlightNewTokens();
    }
    
    updateDiscoveryWidgets(tokens) {
        // Update discovery rate
        const rateElement = document.querySelector('#discoveryRate');
        if (rateElement) {
            rateElement.textContent = `${tokens.length} tokens/min`;
        }
        
        // Update scan status
        const statusElement = document.querySelector('#scanStatus');
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="text-success">
                    <i class="bi bi-check-circle"></i> Active
                </span>
            `;
        }
    }
    
    updateTradingMetrics(data) {
        // Update success rate if element exists
        const successRateElement = document.querySelector('#successRate');
        if (successRateElement) {
            successRateElement.textContent = `${data.success_rate}%`;
        }
        
        // Update total trades
        const totalTradesElement = document.querySelector('#totalTrades');
        if (totalTradesElement) {
            totalTradesElement.textContent = data.total_trades;
        }
    }
    
    updateArbitrageDisplay(count) {
        const arbElements = document.querySelectorAll('[data-widget="arbitrage-ops"] .widget-value');
        arbElements.forEach(element => {
            element.textContent = count;
            this.animateCounterUpdate(element);
        });
    }
    
    setupWebSocket() {
        // WebSocket connection for real-time updates
        // Note: This is a placeholder - implement when WebSocket endpoint is available
        console.log('🔌 WebSocket setup placeholder - implement when backend supports it');
        
        // Simulate real-time updates for now
        setInterval(() => {
            this.simulateRealTimeUpdate();
        }, 10000); // Every 10 seconds
    }
    
    simulateRealTimeUpdate() {
        // Simulate new token discovery
        if (Math.random() > 0.7) {
            this.updateCounters.tokensDiscovered += Math.floor(Math.random() * 3) + 1;
            this.showNewTokenAlert();
        }
        
        // Simulate arbitrage opportunities
        if (Math.random() > 0.8) {
            this.updateCounters.arbitrageOps += 1;
            this.showArbitrageAlert();
        }
        
        // Update displays
        this.updateStatsDisplay({
            portfolio_value: this.updateCounters.portfolioValue,
            daily_pnl: 3241.87,
            trades_today: this.updateCounters.activeTrades
        });
    }
    
    setupAutoRefresh() {
        setInterval(async () => {
            if (this.isConnected) {
                await this.updateDashboardStats();
                await this.updateTokenDiscovery();
                await this.updateTradingData();
                await this.updateArbitrageData();
                
                this.lastUpdate = new Date();
                this.updateLastUpdatedTime();
            }
        }, this.updateInterval);
    }
    
    replaceLoadingText() {
        // Replace any remaining "Loading..." text with actual data or placeholders
        const loadingElements = document.querySelectorAll('*:not(script):not(style)');
        
        loadingElements.forEach(element => {
            if (element.textContent === 'Loading...' || 
                element.textContent === 'Loading…' ||
                element.textContent.includes('Loading')) {
                
                const parent = element.closest('[data-widget]');
                if (parent) {
                    const widgetType = parent.dataset.widget;
                    
                    switch (widgetType) {
                        case 'tokens-discovered':
                            element.textContent = this.updateCounters.tokensDiscovered;
                            break;
                        case 'active-trades':
                            element.textContent = this.updateCounters.activeTrades;
                            break;
                        case 'arbitrage-ops':
                            element.textContent = this.updateCounters.arbitrageOps;
                            break;
                        default:
                            element.textContent = '--';
                    }
                }
            }
        });
    }
    
    showTokenTableError() {
        const tableBody = document.querySelector('tbody');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-3">
                        <i class="bi bi-exclamation-triangle text-warning"></i>
                        Unable to load token data. <a href="#" onclick="dashboardLive.updateTokenDiscovery()">Retry</a>
                    </td>
                </tr>
            `;
        }
    }
    
    highlightNewTokens() {
        // Add highlight animation to new tokens
        const tokenRows = document.querySelectorAll('.token-row');
        tokenRows.forEach((row, index) => {
            if (index < 3) { // Highlight first 3 as "new"
                row.style.animation = 'highlight 2s ease-in-out';
            }
        });
    }
    
    showNewTokenAlert() {
        this.showAlert('success', 'New Token Discovered!', 'High-potential token found and analyzed.', 3000);
    }
    
    showArbitrageAlert() {
        this.showAlert('info', 'Arbitrage Opportunity', 'Cross-DEX price difference detected.', 3000);
    }
    
    showAlert(type, title, message, duration = 5000) {
        const alertsContainer = document.querySelector('#liveAlerts') || 
                               document.querySelector('.live-alerts');
        
        if (alertsContainer) {
            const alertId = 'alert-' + Date.now();
            const alertHtml = `
                <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                    <strong>${title}</strong> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            alertsContainer.insertAdjacentHTML('afterbegin', alertHtml);
            
            // Auto-dismiss after duration
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) {
                    alert.remove();
                }
            }, duration);
        }
    }
    
    animateCounterUpdate(element) {
        element.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.textContent = 'Online';
                statusElement.className = 'connection-status text-success';
            } else {
                statusElement.textContent = 'Reconnecting...';
                statusElement.className = 'connection-status text-warning';
            }
        }
    }
    
    updateLastUpdatedTime() {
        const timeElement = document.querySelector('.last-update-time');
        if (timeElement && this.lastUpdate) {
            timeElement.textContent = this.lastUpdate.toLocaleTimeString();
        }
    }
    
    handleConnectionError() {
        this.isConnected = false;
        this.retryAttempts++;
        
        this.updateConnectionStatus(false);
        
        if (this.retryAttempts < this.maxRetries) {
            setTimeout(() => {
                console.log(`🔄 Retrying connection (${this.retryAttempts}/${this.maxRetries})...`);
                this.startLiveUpdates();
            }, 5000 * this.retryAttempts);
        } else {
            console.error('❌ Max retry attempts reached');
            this.showAlert('danger', 'Connection Lost', 'Unable to connect to live data feed.', 10000);
        }
    }
    
    // Utility methods
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 6
        }).format(value);
    }
    
    formatNumber(value) {
        if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'K';
        }
        return value.toString();
    }
    
    getRiskLevel(score) {
        if (score <= 2) return 'Low Risk';
        if (score <= 4) return 'Medium Risk';
        if (score <= 6) return 'High Risk';
        return 'Critical';
    }
    
    getRiskColor(level) {
        switch (level) {
            case 'Low Risk': return 'success';
            case 'Medium Risk': return 'warning';
            case 'High Risk': return 'danger';
            default: return 'dark';
        }
    }
}

// Global functions for token actions
window.analyzeToken = function(address) {
    console.log(`🔍 Analyzing token: ${address}`);
    // Show analysis modal or navigate to analysis page
    alert(`Analyzing token: ${address.substring(0, 10)}...`);
};

window.tradeToken = function(address) {
    console.log(`💱 Trading token: ${address}`);
    // Show trading modal or execute trade
    alert(`Initiating trade for: ${address.substring(0, 10)}...`);
};

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes highlight {
        0% { background-color: rgba(13, 202, 240, 0.2); }
        100% { background-color: transparent; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .token-row:hover {
        background-color: rgba(0, 123, 255, 0.05);
    }
`;
document.head.appendChild(style);

// Initialize live updates when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboardLive = new DashboardLiveUpdates();
    });
} else {
    window.dashboardLive = new DashboardLiveUpdates();
}

console.log('📡 Dashboard Live Updates script loaded');