/**
 * Enhanced Dashboard JavaScript with WebSocket Integration
 * File: frontend/static/js/dashboard-enhanced.js
 * 
 * Provides real-time dashboard functionality with WebSocket communication.
 * Handles live trading data, portfolio updates, and system notifications.
 */

class EnhancedDashboard {
    constructor() {
        this.ws = null;
        this.clientId = this.generateClientId();
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        
        // Data stores
        this.portfolioData = {};
        this.tradingData = {};
        this.systemData = {};
        
        // UI update intervals
        this.updateIntervals = {};
        
        // Chart instances
        this.charts = {};
        
        // Event listeners
        this.eventListeners = new Map();
        
        this.initialize();
    }
    
    async initialize() {
        console.log('🚀 Initializing Enhanced Dashboard...');
        
        try {
            // Initialize UI components
            this.initializeUI();
            
            // Setup WebSocket connection
            await this.initializeWebSocket();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Start periodic updates
            this.startPeriodicUpdates();
            
            console.log('✅ Enhanced Dashboard initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize Enhanced Dashboard:', error);
            this.showNotification('Initialization failed', 'error');
        }
    }
    
    generateClientId() {
        return `dashboard_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    async initializeWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/dashboard/${this.clientId}`;
            
            console.log('🔌 Connecting to WebSocket:', wsUrl);
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.showNotification('Connected to live data feed', 'success');
                
                // Subscribe to all relevant channels
                this.subscribeToChannels();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('🔌 WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.showNotification('Disconnected from live data feed', 'warning');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.showNotification('WebSocket connection error', 'error');
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            throw error;
        }
    }
    
    subscribeToChannels() {
        const subscriptions = [
            'dashboard',
            'trading',
            'portfolio', 
            'alerts',
            'system'
        ];
        
        subscriptions.forEach(subscription => {
            this.sendWebSocketMessage({
                type: 'subscribe',
                data: { subscription: subscription }
            });
        });
    }
    
    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message received:', data.type);
        
        switch (data.type) {
            case 'portfolio_update':
                this.handlePortfolioUpdate(data.data);
                break;
            case 'trading_status':
                this.handleTradingStatusUpdate(data.data);
                break;
            case 'trade_execution':
                this.handleTradeExecution(data.data);
                break;
            case 'token_discovery':
                this.handleTokenDiscovery(data.data);
                break;
            case 'arbitrage_alert':
                this.handleArbitrageAlert(data.data);
                break;
            case 'system_health':
                this.handleSystemHealthUpdate(data.data);
                break;
            case 'heartbeat':
                this.handleHeartbeat(data.data);
                break;
            case 'error':
                this.handleError(data.data);
                break;
            default:
                console.warn('Unknown WebSocket message type:', data.type);
        }
    }
    
    handlePortfolioUpdate(data) {
        this.portfolioData = { ...this.portfolioData, ...data };
        this.updatePortfolioUI(data);
        this.triggerEvent('portfolio_updated', data);
    }
    
    handleTradingStatusUpdate(data) {
        this.tradingData = { ...this.tradingData, ...data };
        this.updateTradingUI(data);
        this.triggerEvent('trading_updated', data);
    }
    
    handleTradeExecution(data) {
        this.addActivityLogEntry(
            `🔄 Trade executed: ${data.trade?.symbol || 'Unknown'} - ${data.trade?.status || 'Unknown'}`,
            data.trade?.status === 'success' ? 'success' : 'warning'
        );
        
        // Update trade metrics
        if (data.metrics) {
            this.updateTradingMetrics(data.metrics);
        }
        
        this.triggerEvent('trade_executed', data);
        this.showNotification(`Trade executed: ${data.trade?.symbol || 'Unknown'}`, 'info');
    }
    
    handleTokenDiscovery(data) {
        const token = data.token || data;
        this.addActivityLogEntry(
            `🎯 New token discovered: ${token.symbol || 'Unknown'} (${this.truncateAddress(token.address)})`,
            'info'
        );
        
        // Update token counter
        this.incrementCounter('tokens-discovered');
        
        this.triggerEvent('token_discovered', data);
        this.showNotification(`New token: ${token.symbol || 'Unknown'}`, 'info');
    }
    
    handleArbitrageAlert(data) {
        const opportunity = data.opportunity || data;
        const profitPercent = opportunity.profit_percentage || 0;
        
        this.addActivityLogEntry(
            `💰 Arbitrage opportunity: ${profitPercent.toFixed(2)}% profit potential`,
            'success'
        );
        
        // Update arbitrage counter
        this.incrementCounter('arbitrage-opportunities');
        
        this.triggerEvent('arbitrage_found', data);
        this.showNotification(`Arbitrage: ${profitPercent.toFixed(2)}% profit`, 'success');
    }
    
    handleSystemHealthUpdate(data) {
        this.systemData = { ...this.systemData, ...data };
        this.updateSystemHealthUI(data);
        this.triggerEvent('system_updated', data);
    }
    
    handleHeartbeat(data) {
        // Update connection timestamp
        this.lastHeartbeat = new Date();
        console.log('💓 Heartbeat received');
    }
    
    handleError(data) {
        console.error('WebSocket error:', data);
        this.showNotification(data.error || 'Unknown error', 'error');
    }
    
    updatePortfolioUI(data) {
        // Update portfolio value
        if (data.portfolio?.total_value !== undefined) {
            this.updateElement('portfolio-value', this.formatCurrency(data.portfolio.total_value));
        }
        
        if (data.metrics) {
            const metrics = data.metrics;
            
            // Update daily change
            if (metrics.daily_change !== undefined) {
                const isPositive = metrics.daily_change >= 0;
                const changeEl = document.getElementById('portfolio-change');
                if (changeEl) {
                    changeEl.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
                    changeEl.innerHTML = `
                        <i class="bi bi-arrow-${isPositive ? 'up' : 'down'}"></i> 
                        ${isPositive ? '+' : ''}${this.formatCurrency(Math.abs(metrics.daily_change))} 
                        (${(metrics.daily_change_percent || 0).toFixed(2)}%)
                    `;
                }
            }
            
            // Update available balance
            if (metrics.available_balance !== undefined) {
                this.updateElement('available-balance', this.formatCurrency(metrics.available_balance));
            }
            
            // Update positions
            if (metrics.top_positions) {
                this.updatePositionsTable(metrics.top_positions);
            }
        }
    }
    
    updateTradingUI(data) {
        // Update trade counts
        if (data.total_trades_today !== undefined) {
            this.updateElement('trades-today', data.total_trades_today);
        }
        
        if (data.successful_trades !== undefined) {
            this.updateElement('successful-trades', data.successful_trades);
        }
        
        // Update success rate
        if (data.success_rate !== undefined) {
            this.updateElement('success-rate', `${data.success_rate.toFixed(1)}%`);
        }
        
        // Update active strategies
        if (data.active_strategies) {
            this.updateElement('active-strategies', data.active_strategies.length);
            this.updateStrategiesList(data.active_strategies);
        }
        
        // Update trading status
        if (data.is_running !== undefined) {
            this.updateTradingStatus(data.is_running);
        }
    }
    
    updateSystemHealthUI(data) {
        // Update system metrics
        if (data.memory_usage !== undefined) {
            this.updateElement('memory-usage', `${data.memory_usage.toFixed(1)}%`);
        }
        
        if (data.cpu_usage !== undefined) {
            this.updateElement('cpu-usage', `${data.cpu_usage.toFixed(1)}%`);
        }
        
        if (data.uptime) {
            this.updateElement('system-uptime', data.uptime);
        }
        
        // Update connection count
        if (data.active_connections !== undefined) {
            this.updateElement('active-connections', data.active_connections);
        }
        
        // Update blockchain connections
        if (data.blockchain_connections) {
            this.updateBlockchainStatus(data.blockchain_connections);
        }
    }
    
    updateTradingMetrics(metrics) {
        Object.entries(metrics).forEach(([key, value]) => {
            const element = document.getElementById(`metric-${key.replace(/_/g, '-')}`);
            if (element) {
                if (typeof value === 'number') {
                    element.textContent = key.includes('rate') || key.includes('percent') 
                        ? `${value.toFixed(2)}%` 
                        : this.formatNumber(value);
                } else {
                    element.textContent = value;
                }
            }
        });
    }
    
    updatePositionsTable(positions) {
        const tableBody = document.getElementById('positions-table-body');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        positions.forEach(position => {
            const row = document.createElement('tr');
            const isPositive = (position.change_24h || 0) >= 0;
            
            row.innerHTML = `
                <td>
                    <strong>${position.symbol || 'Unknown'}</strong>
                    <br>
                    <small class="text-muted">${this.truncateAddress(position.address)}</small>
                </td>
                <td>${this.formatCurrency(position.value || 0)}</td>
                <td class="${isPositive ? 'text-success' : 'text-danger'}">
                    <i class="bi bi-arrow-${isPositive ? 'up' : 'down'}"></i>
                    ${(position.change_24h || 0).toFixed(2)}%
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    }
    
    updateStrategiesList(strategies) {
        const container = document.getElementById('strategies-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        strategies.forEach(strategy => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success me-1';
            badge.textContent = strategy;
            container.appendChild(badge);
        });
    }
    
    updateTradingStatus(isRunning) {
        const statusEl = document.getElementById('trading-status');
        if (statusEl) {
            statusEl.textContent = isRunning ? 'Running' : 'Stopped';
            statusEl.className = `badge ${isRunning ? 'bg-success' : 'bg-danger'}`;
        }
        
        // Update start/stop buttons
        const startBtn = document.getElementById('start-trading-btn');
        const stopBtn = document.getElementById('stop-trading-btn');
        
        if (startBtn) startBtn.disabled = isRunning;
        if (stopBtn) stopBtn.disabled = !isRunning;
    }
    
    updateBlockchainStatus(connections) {
        Object.entries(connections).forEach(([network, status]) => {
            const element = document.getElementById(`${network}-status`);
            if (element) {
                element.textContent = status;
                element.className = `badge ${status === 'connected' ? 'bg-success' : 'bg-danger'}`;
            }
        });
    }
    
    incrementCounter(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            const current = parseInt(element.textContent) || 0;
            element.textContent = current + 1;
        }
    }
    
    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }
    
    addActivityLogEntry(message, type = 'info') {
        const logContainer = document.getElementById('activity-log');
        if (!logContainer) return;
        
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        entry.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-message">${message}</span>
        `;
        
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Limit log entries to prevent memory issues
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');
        const wsStatus = document.getElementById('ws-status');
        
        if (statusDot) {
            statusDot.className = `status-dot ${connected ? 'status-success' : 'status-danger'}`;
        }
        
        if (statusText) {
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
        }
        
        if (wsStatus) {
            wsStatus.textContent = connected ? 'Connected' : 'Disconnected';
            wsStatus.className = `badge ${connected ? 'bg-success' : 'bg-danger'}`;
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this.showNotification('Connection failed - max retries reached', 'error');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * this.reconnectAttempts;
        
        console.log(`🔄 Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
        this.showNotification(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, 'info');
        
        setTimeout(() => {
            this.initializeWebSocket();
        }, delay);
    }
    
    sendWebSocketMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
            console.log('📤 Sent WebSocket message:', message);
        } else {
            console.warn('Cannot send message - WebSocket not connected');
        }
    }
    
    sendCommand(command, data = {}) {
        this.sendWebSocketMessage({
            type: 'command',
            data: { command, ...data }
        });
    }
    
    setupEventListeners() {
        // Trading control buttons
        document.getElementById('start-trading-btn')?.addEventListener('click', () => {
            this.sendCommand('start_trading');
            this.addActivityLogEntry('🚀 Starting trading engine...', 'info');
        });
        
        document.getElementById('stop-trading-btn')?.addEventListener('click', () => {
            this.sendCommand('stop_trading');
            this.addActivityLogEntry('🛑 Stopping trading engine...', 'warning');
        });
        
        // Data refresh button
        document.getElementById('refresh-data-btn')?.addEventListener('click', () => {
            this.sendCommand('refresh_data');
            this.addActivityLogEntry('🔄 Refreshing data...', 'info');
        });
        
        // Clear activity log button
        document.getElementById('clear-log-btn')?.addEventListener('click', () => {
            this.clearActivityLog();
        });
    }
    
    initializeUI() {
        // Initialize any UI components that need setup
        this.addActivityLogEntry('📊 Dashboard initialized', 'success');
    }
    
    startPeriodicUpdates() {
        // Heartbeat every 30 seconds
        this.updateIntervals.heartbeat = setInterval(() => {
            this.sendWebSocketMessage({
                type: 'heartbeat',
                data: { timestamp: new Date().toISOString() }
            });
        }, 30000);
        
        // Update timestamps every second
        this.updateIntervals.timestamp = setInterval(() => {
            this.updateTimestamps();
        }, 1000);
    }
    
    updateTimestamps() {
        // Update any relative timestamps in the UI
        const timestampElements = document.querySelectorAll('[data-timestamp]');
        timestampElements.forEach(element => {
            const timestamp = element.getAttribute('data-timestamp');
            if (timestamp) {
                element.textContent = this.getRelativeTime(new Date(timestamp));
            }
        });
    }
    
    clearActivityLog() {
        const logContainer = document.getElementById('activity-log');
        if (logContainer) {
            logContainer.innerHTML = '';
            this.addActivityLogEntry('📋 Activity log cleared', 'info');
        }
    }
    
    // Event system
    addEventListener(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }
    
    triggerEvent(event, data) {
        const listeners = this.eventListeners.get(event);
        if (listeners) {
            listeners.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }
    
    // Utility methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(num);
    }
    
    truncateAddress(address) {
        if (!address) return 'N/A';
        return `${address.slice(0, 6)}...${address.slice(-4)}`;
    }
    
    getRelativeTime(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system - can be enhanced
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // You could integrate with a toast notification library here
        const notification = {
            message,
            type,
            timestamp: new Date()
        };
        
        this.triggerEvent('notification', notification);
    }
    
    // Cleanup
    destroy() {
        // Clear intervals
        Object.values(this.updateIntervals).forEach(interval => {
            clearInterval(interval);
        });
        
        // Close WebSocket
        if (this.ws) {
            this.ws.close();
        }
        
        // Clear event listeners
        this.eventListeners.clear();
        
        console.log('🧹 Enhanced Dashboard destroyed');
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Enhanced Dashboard...');
    window.enhancedDashboard = new EnhancedDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.enhancedDashboard) {
        window.enhancedDashboard.destroy();
    }
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedDashboard;
}