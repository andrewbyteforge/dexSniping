/**
 * WebSocket Integration for Existing Dashboard
 * File: frontend/static/js/websocket-integration.js
 * 
 * Adds live WebSocket functionality to the existing dashboard without changing styling.
 */

class DashboardWebSocketIntegration {
    constructor() {
        this.ws = null;
        this.clientId = 'dashboard_' + Math.random().toString(36).substr(2, 9);
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        // Only initialize if we're on the dashboard page
        if (this.isDashboardPage()) {
            this.initializeWebSocket();
            this.setupStatusIndicator();
        }
    }
    
    isDashboardPage() {
        // Check if we're on the dashboard page by looking for dashboard-specific elements
        return document.getElementById('portfolioValue') || 
               document.getElementById('dailyPnL') || 
               window.location.pathname.includes('dashboard');
    }
    
    initializeWebSocket() {
        try {
            const wsUrl = `ws://${window.location.host}/api/v1/ws/dashboard/${this.clientId}`;
            console.log('🔌 Connecting to WebSocket:', wsUrl);
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.logActivity('Connected to live data feed');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };
            
            this.ws.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.logActivity('Disconnected from live data feed');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.logActivity('WebSocket connection error');
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('📨 Received WebSocket message:', data.type);
        
        switch (data.type) {
            case 'portfolio_update':
                this.updatePortfolioDisplay(data.data);
                break;
            case 'trading_status':
                this.updateTradingStatus(data.data);
                break;
            case 'trade_execution':
                this.handleTradeNotification(data.data);
                break;
            case 'token_discovery':
                this.handleTokenDiscovery(data.data);
                break;
            case 'arbitrage_alert':
                this.handleArbitrageAlert(data.data);
                break;
            case 'system_health':
                this.updateSystemHealth(data.data);
                break;
            case 'heartbeat':
                console.log('💓 Heartbeat received');
                break;
        }
    }
    
    updatePortfolioDisplay(data) {
        // Update existing portfolio elements if they exist
        if (data.portfolio) {
            const portfolioElement = document.getElementById('portfolioValue');
            if (portfolioElement) {
                portfolioElement.textContent = this.formatCurrency(data.portfolio.total_value);
                this.animateElement(portfolioElement);
            }
        }
        
        if (data.metrics && data.metrics.daily_change !== undefined) {
            const pnlElement = document.getElementById('dailyPnL');
            if (pnlElement) {
                const change = data.metrics.daily_change;
                const isPositive = change >= 0;
                pnlElement.textContent = (isPositive ? '+' : '') + this.formatCurrency(Math.abs(change));
                pnlElement.className = pnlElement.className.replace(/text-(success|danger)/, '') + 
                                     (isPositive ? ' text-success' : ' text-danger');
                this.animateElement(pnlElement);
            }
        }
        
        this.logActivity('Portfolio data updated');
    }
    
    updateTradingStatus(data) {
        // Update trading-related elements
        const successRateElement = document.getElementById('successRate');
        if (successRateElement && data.success_rate !== undefined) {
            successRateElement.textContent = data.success_rate.toFixed(1) + '%';
            this.animateElement(successRateElement);
        }
        
        const activeTradesElement = document.getElementById('activeTrades');
        if (activeTradesElement && data.total_trades_today !== undefined) {
            activeTradesElement.textContent = data.total_trades_today;
            this.animateElement(activeTradesElement);
        }
        
        this.logActivity('Trading status updated');
    }
    
    handleTradeNotification(data) {
        const trade = data.trade || data;
        const message = `Trade executed: ${trade.symbol || 'Unknown'} - ${trade.status || 'Unknown'}`;
        this.logActivity(message);
        this.showNotification(message, trade.status === 'success' ? 'success' : 'warning');
    }
    
    handleTokenDiscovery(data) {
        const token = data.token || data;
        const message = `New token discovered: ${token.symbol || 'Unknown'}`;
        this.logActivity(message);
        this.showNotification(message, 'info');
    }
    
    handleArbitrageAlert(data) {
        const opportunity = data.opportunity || data;
        const profit = opportunity.profit_percentage || 0;
        const message = `Arbitrage opportunity: ${profit.toFixed(2)}% profit potential`;
        this.logActivity(message);
        this.showNotification(message, 'success');
    }
    
    updateSystemHealth(data) {
        // Update system health indicators if they exist
        if (data.memory_usage !== undefined) {
            const memoryElement = document.getElementById('memoryUsage');
            if (memoryElement) {
                memoryElement.textContent = data.memory_usage.toFixed(1) + '%';
            }
        }
        
        if (data.cpu_usage !== undefined) {
            const cpuElement = document.getElementById('cpuUsage');
            if (cpuElement) {
                cpuElement.textContent = data.cpu_usage.toFixed(1) + '%';
            }
        }
    }
    
    setupStatusIndicator() {
        // Add a small connection status indicator to the existing dashboard
        const statusIndicator = document.createElement('div');
        statusIndicator.id = 'websocket-status';
        statusIndicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 8px 12px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 20px;
            font-size: 12px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.3s ease;
        `;
        
        statusIndicator.innerHTML = `
            <div id="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #ffc107;"></div>
            <span id="status-text">Connecting...</span>
        `;
        
        document.body.appendChild(statusIndicator);
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot && statusText) {
            if (connected) {
                statusDot.style.background = '#28a745';
                statusText.textContent = 'Live';
            } else {
                statusDot.style.background = '#dc3545';
                statusText.textContent = 'Disconnected';
            }
        }
        
        // Update existing live indicator if it exists
        const liveIndicator = document.querySelector('.live-indicator');
        if (liveIndicator) {
            const dot = liveIndicator.querySelector('.bi-dot, i');
            if (dot) {
                dot.className = connected ? 'bi bi-dot text-success' : 'bi bi-dot text-danger';
            }
        }
        
        // Update last update time
        const lastUpdateElement = document.getElementById('lastUpdateTime');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = new Date().toLocaleTimeString();
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, 2000 * this.reconnectAttempts);
        } else {
            console.error('❌ Max reconnection attempts reached');
            this.logActivity('Connection failed - max retries reached');
        }
    }
    
    logActivity(message) {
        console.log(`[${new Date().toLocaleTimeString()}] ${message}`);
        
        // Try to add to existing activity log if it exists
        const activityLog = document.getElementById('activityLog') || 
                           document.getElementById('activity-log') ||
                           document.querySelector('.activity-feed');
        
        if (activityLog) {
            const entry = document.createElement('div');
            entry.className = 'activity-entry';
            entry.innerHTML = `<small class="text-muted">[${new Date().toLocaleTimeString()}]</small> ${message}`;
            entry.style.cssText = 'padding: 4px 0; border-bottom: 1px solid #eee; font-size: 0.9em;';
            
            activityLog.appendChild(entry);
            activityLog.scrollTop = activityLog.scrollHeight;
            
            // Keep only last 50 entries
            while (activityLog.children.length > 50) {
                activityLog.removeChild(activityLog.firstChild);
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Create a temporary notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            padding: 12px 16px;
            background: ${type === 'success' ? '#d4edda' : type === 'warning' ? '#fff3cd' : '#d1ecf1'};
            color: ${type === 'success' ? '#155724' : type === 'warning' ? '#856404' : '#0c5460'};
            border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'warning' ? '#ffeaa7' : '#bee5eb'};
            border-radius: 4px;
            font-size: 14px;
            z-index: 1001;
            max-width: 300px;
            word-wrap: break-word;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
        
        // Add CSS animations if they don't exist
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    animateElement(element) {
        // Add a subtle animation to updated elements
        element.style.transform = 'scale(1.05)';
        element.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing WebSocket integration for existing dashboard...');
    new DashboardWebSocketIntegration();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardWebSocketIntegration;
}