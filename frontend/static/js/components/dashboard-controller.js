/**
 * Dashboard Controller Module
 * File: frontend/static/js/components/dashboard-controller.js
 * 
 * Orchestrates all dashboard components and manages their interactions.
 * Handles data flow, updates, and communication between different dashboard elements.
 */

class DashboardController {
    constructor(app) {
        this.app = app;
        this.isInitialized = false;
        this.isRefreshing = false;
        this.refreshInterval = null;
        this.lastUpdateTime = null;
        
        // Component references
        this.components = {
            statsCards: null,
            tokenDiscovery: null,
            liveAlerts: null,
            charts: null
        };
        
        // Dashboard state
        this.state = {
            stats: null,
            tokens: [],
            alerts: [],
            isOnline: true,
            lastError: null
        };
        
        // Configuration
        this.config = {
            refreshInterval: window.APP_CONSTANTS?.REFRESH_INTERVALS?.STATS || 10000,
            maxRetries: 3,
            retryDelay: 1000,
            enableAutoRefresh: true
        };
        
        console.log('🎛️ Dashboard Controller created');
    }

    /**
     * Initialize the dashboard controller
     */
    async init() {
        try {
            console.log('🔧 Initializing Dashboard Controller...');
            
            // Initialize components
            await this.initializeComponents();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            // Start auto-refresh if enabled
            if (this.config.enableAutoRefresh) {
                this.startAutoRefresh();
            }
            
            this.isInitialized = true;
            console.log('✅ Dashboard Controller initialized');
            
            // Emit initialization event
            this.app.events.dispatchEvent(new CustomEvent('dashboard:initialized'));
            
        } catch (error) {
            console.error('❌ Dashboard Controller initialization failed:', error);
            this.handleError('Initialization failed', error);
            throw error;
        }
    }

    /**
     * Initialize dashboard components
     */
    async initializeComponents() {
        try {
            console.log('🔧 Initializing dashboard components...');
            
            // Initialize Stats Cards component
            if (typeof window.StatsCards !== 'undefined') {
                this.components.statsCards = window.StatsCards;
                console.log('✅ Stats Cards component connected');
            } else {
                console.warn('⚠️ Stats Cards component not found');
            }
            
            // Initialize Token Discovery component
            if (typeof window.TokenDiscoveryTable !== 'undefined') {
                this.components.tokenDiscovery = window.TokenDiscoveryTable;
                console.log('✅ Token Discovery component connected');
            } else {
                console.warn('⚠️ Token Discovery component not found');
            }
            
            // Initialize Live Alerts component
            if (typeof window.LiveAlerts !== 'undefined') {
                this.components.liveAlerts = window.LiveAlerts;
                console.log('✅ Live Alerts component connected');
            } else {
                console.warn('⚠️ Live Alerts component not found');
            }
            
            console.log('✅ Dashboard components initialized');
            
        } catch (error) {
            console.error('❌ Component initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup event listeners for component communication
     */
    setupEventListeners() {
        try {
            console.log('🔧 Setting up event listeners...');
            
            // Listen for app events
            this.app.events.addEventListener('app:online', () => {
                this.handleConnectionChange(true);
            });
            
            this.app.events.addEventListener('app:offline', () => {
                this.handleConnectionChange(false);
            });
            
            // Listen for WebSocket events
            if (this.app.websocket) {
                this.app.websocket.on('stats_update', (data) => {
                    this.handleStatsUpdate(data);
                });
                
                this.app.websocket.on('token_discovery', (data) => {
                    this.handleTokenUpdate(data);
                });
                
                this.app.websocket.on('live_alert', (data) => {
                    this.handleAlertUpdate(data);
                });
                
                this.app.websocket.on('error', (error) => {
                    this.handleWebSocketError(error);
                });
            }
            
            // Listen for component events
            document.addEventListener('stats:refresh', () => {
                this.refreshStats();
            });
            
            document.addEventListener('stats:error', (event) => {
                this.handleComponentError('Stats Cards', event.detail);
            });
            
            document.addEventListener('tokens:discovery:start', () => {
                this.handleTokenDiscoveryStart();
            });
            
            document.addEventListener('tokens:discovery:stop', () => {
                this.handleTokenDiscoveryStop();
            });
            
            document.addEventListener('alerts:new', (event) => {
                this.handleNewAlert(event.detail);
            });
            
            // Page visibility change
            document.addEventListener('visibilitychange', () => {
                this.handleVisibilityChange();
            });
            
            console.log('✅ Event listeners setup complete');
            
        } catch (error) {
            console.error('❌ Event listener setup failed:', error);
            throw error;
        }
    }

    /**
     * Load initial dashboard data
     */
    async loadInitialData() {
        try {
            console.log('🔧 Loading initial dashboard data...');
            
            // Load dashboard stats
            await this.loadStats();
            
            // Load recent tokens
            await this.loadTokens();
            
            // Load recent alerts
            await this.loadAlerts();
            
            this.lastUpdateTime = new Date();
            console.log('✅ Initial data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
            this.handleError('Failed to load initial data', error);
        }
    }

    /**
     * Load dashboard statistics
     */
    async loadStats() {
        try {
            console.log('📊 Loading dashboard stats...');
            
            if (!this.app.apiClient) {
                throw new Error('API Client not available');
            }
            
            const response = await this.app.apiClient.get('/dashboard/stats');
            
            if (response && response.data) {
                this.state.stats = response.data;
                
                // Update Stats Cards component
                if (this.components.statsCards) {
                    this.updateStatsCards(response.data);
                }
                
                console.log('✅ Dashboard stats loaded');
            }
            
        } catch (error) {
            console.error('❌ Failed to load stats:', error);
            this.handleError('Failed to load statistics', error);
        }
    }

    /**
     * Load token discovery data
     */
    async loadTokens() {
        try {
            console.log('🪙 Loading token data...');
            
            if (!this.app.apiClient) {
                throw new Error('API Client not available');
            }
            
            const response = await this.app.apiClient.get('/tokens/discover?limit=10');
            
            if (response && response.data && Array.isArray(response.data.tokens)) {
                this.state.tokens = response.data.tokens;
                
                // Update Token Discovery component
                if (this.components.tokenDiscovery) {
                    this.updateTokenDiscovery(response.data.tokens);
                }
                
                console.log(`✅ Loaded ${response.data.tokens.length} tokens`);
            }
            
        } catch (error) {
            console.error('❌ Failed to load tokens:', error);
            this.handleError('Failed to load token data', error);
        }
    }

    /**
     * Load recent alerts
     */
    async loadAlerts() {
        try {
            console.log('🚨 Loading alerts...');
            
            // For now, use mock data since alerts endpoint might not exist yet
            const mockAlerts = [
                {
                    id: 'alert_1',
                    type: 'trading',
                    title: 'High Volume Detected',
                    message: 'PEPE showing unusual trading volume',
                    timestamp: new Date().toISOString(),
                    severity: 'info'
                }
            ];
            
            this.state.alerts = mockAlerts;
            
            // Update Live Alerts component
            if (this.components.liveAlerts) {
                this.updateLiveAlerts(mockAlerts);
            }
            
            console.log(`✅ Loaded ${mockAlerts.length} alerts`);
            
        } catch (error) {
            console.error('❌ Failed to load alerts:', error);
            this.handleError('Failed to load alerts', error);
        }
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        if (this.refreshInterval) {
            this.stopAutoRefresh();
        }
        
        console.log(`🔄 Starting auto-refresh (${this.config.refreshInterval}ms)`);
        
        this.refreshInterval = setInterval(() => {
            if (!document.hidden && this.state.isOnline) {
                this.refreshAll();
            }
        }, this.config.refreshInterval);
    }

    /**
     * Stop auto-refresh timer
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('⏹️ Auto-refresh stopped');
        }
    }

    /**
     * Refresh all dashboard data
     */
    async refreshAll() {
        if (this.isRefreshing) {
            console.log('🔄 Refresh already in progress, skipping...');
            return;
        }
        
        try {
            this.isRefreshing = true;
            console.log('🔄 Refreshing all dashboard data...');
            
            // Parallel data loading for better performance
            const promises = [
                this.loadStats().catch(console.error),
                this.loadTokens().catch(console.error),
                this.loadAlerts().catch(console.error)
            ];
            
            await Promise.allSettled(promises);
            
            this.lastUpdateTime = new Date();
            this.updateLastRefreshTime();
            
            console.log('✅ Dashboard refresh complete');
            
            // Emit refresh event
            this.app.events.dispatchEvent(new CustomEvent('dashboard:refreshed'));
            
        } catch (error) {
            console.error('❌ Dashboard refresh failed:', error);
            this.handleError('Refresh failed', error);
        } finally {
            this.isRefreshing = false;
        }
    }

    /**
     * Refresh only statistics
     */
    async refreshStats() {
        try {
            console.log('📊 Refreshing stats...');
            await this.loadStats();
            
        } catch (error) {
            console.error('❌ Stats refresh failed:', error);
            this.handleError('Stats refresh failed', error);
        }
    }

    // Event Handlers

    /**
     * Handle connection status change
     */
    handleConnectionChange(isOnline) {
        console.log(`🌐 Connection status: ${isOnline ? 'online' : 'offline'}`);
        
        this.state.isOnline = isOnline;
        
        if (isOnline) {
            // Resume auto-refresh when back online
            if (this.config.enableAutoRefresh && !this.refreshInterval) {
                this.startAutoRefresh();
            }
            
            // Immediate refresh when reconnected
            this.refreshAll();
        } else {
            // Pause auto-refresh when offline
            this.stopAutoRefresh();
        }
        
        // Update UI to show connection status
        this.updateConnectionStatus(isOnline);
    }

    /**
     * Handle WebSocket stats update
     */
    handleStatsUpdate(data) {
        try {
            console.log('📊 Received stats update via WebSocket');
            
            this.state.stats = { ...this.state.stats, ...data };
            
            // Update Stats Cards component
            if (this.components.statsCards) {
                this.updateStatsCards(this.state.stats);
            }
            
        } catch (error) {
            console.error('❌ Failed to handle stats update:', error);
        }
    }

    /**
     * Handle WebSocket token update
     */
    handleTokenUpdate(data) {
        try {
            console.log('🪙 Received token update via WebSocket');
            
            if (data.token) {
                // Add or update token in state
                const existingIndex = this.state.tokens.findIndex(
                    token => token.address === data.token.address
                );
                
                if (existingIndex >= 0) {
                    this.state.tokens[existingIndex] = data.token;
                } else {
                    this.state.tokens.unshift(data.token);
                    // Keep only latest 50 tokens
                    if (this.state.tokens.length > 50) {
                        this.state.tokens = this.state.tokens.slice(0, 50);
                    }
                }
                
                // Update Token Discovery component
                if (this.components.tokenDiscovery) {
                    this.updateTokenDiscovery(this.state.tokens);
                }
            }
            
        } catch (error) {
            console.error('❌ Failed to handle token update:', error);
        }
    }

    /**
     * Handle WebSocket alert update
     */
    handleAlertUpdate(data) {
        try {
            console.log('🚨 Received alert update via WebSocket');
            
            if (data.alert) {
                // Add alert to state
                this.state.alerts.unshift(data.alert);
                
                // Keep only latest 20 alerts
                if (this.state.alerts.length > 20) {
                    this.state.alerts = this.state.alerts.slice(0, 20);
                }
                
                // Update Live Alerts component
                if (this.components.liveAlerts) {
                    this.updateLiveAlerts(this.state.alerts);
                }
            }
            
        } catch (error) {
            console.error('❌ Failed to handle alert update:', error);
        }
    }

    /**
     * Handle WebSocket errors
     */
    handleWebSocketError(error) {
        console.error('🔌 WebSocket error in dashboard:', error);
        
        // Show error notification
        this.showErrorNotification('Real-time connection issue. Retrying...');
        
        // Switch to polling mode temporarily
        if (!this.refreshInterval && this.config.enableAutoRefresh) {
            this.startAutoRefresh();
        }
    }

    /**
     * Handle component errors
     */
    handleComponentError(componentName, error) {
        console.error(`❌ ${componentName} error:`, error);
        
        this.showErrorNotification(`${componentName} error: ${error.message || error}`);
    }

    /**
     * Handle new alert creation
     */
    handleNewAlert(alert) {
        console.log('🚨 New alert created:', alert);
        
        // Add to state
        this.state.alerts.unshift(alert);
        
        // Update component
        if (this.components.liveAlerts) {
            this.updateLiveAlerts(this.state.alerts);
        }
    }

    /**
     * Handle token discovery start
     */
    handleTokenDiscoveryStart() {
        console.log('🔍 Token discovery started');
        
        // Update stats to reflect discovery status
        if (this.state.stats) {
            this.state.stats.discovery_active = true;
            this.updateStatsCards(this.state.stats);
        }
    }

    /**
     * Handle token discovery stop
     */
    handleTokenDiscoveryStop() {
        console.log('⏹️ Token discovery stopped');
        
        // Update stats to reflect discovery status
        if (this.state.stats) {
            this.state.stats.discovery_active = false;
            this.updateStatsCards(this.state.stats);
        }
    }

    /**
     * Handle page visibility change
     */
    handleVisibilityChange() {
        if (document.hidden) {
            console.log('📄 Page hidden, pausing intensive operations');
            // Reduce refresh frequency when page is hidden
        } else {
            console.log('📄 Page visible, resuming normal operations');
            // Immediate refresh when page becomes visible
            if (this.state.isOnline) {
                this.refreshAll();
            }
        }
    }

    // Component Update Methods

    /**
     * Update Stats Cards component
     */
    updateStatsCards(data) {
        try {
            if (this.components.statsCards && typeof this.components.statsCards.updateStats === 'function') {
                this.components.statsCards.updateStats(data);
            }
        } catch (error) {
            console.error('❌ Failed to update stats cards:', error);
        }
    }

    /**
     * Update Token Discovery component
     */
    updateTokenDiscovery(tokens) {
        try {
            if (this.components.tokenDiscovery && typeof this.components.tokenDiscovery.updateTokens === 'function') {
                this.components.tokenDiscovery.updateTokens(tokens);
            }
        } catch (error) {
            console.error('❌ Failed to update token discovery:', error);
        }
    }

    /**
     * Update Live Alerts component
     */
    updateLiveAlerts(alerts) {
        try {
            if (this.components.liveAlerts && typeof this.components.liveAlerts.updateAlerts === 'function') {
                this.components.liveAlerts.updateAlerts(alerts);
            }
        } catch (error) {
            console.error('❌ Failed to update live alerts:', error);
        }
    }

    // UI Update Methods

    /**
     * Update connection status in UI
     */
    updateConnectionStatus(isOnline) {
        try {
            const statusElements = document.querySelectorAll('.connection-status');
            const statusClass = isOnline ? 'text-success' : 'text-danger';
            const statusText = isOnline ? 'Online' : 'Offline';
            
            statusElements.forEach(element => {
                element.className = `connection-status ${statusClass}`;
                element.textContent = statusText;
            });
            
        } catch (error) {
            console.error('❌ Failed to update connection status:', error);
        }
    }

    /**
     * Update last refresh time display
     */
    updateLastRefreshTime() {
        try {
            const timeElements = document.querySelectorAll('.last-update-time');
            const timeString = this.lastUpdateTime ? 
                this.app.formatters?.formatTime(this.lastUpdateTime) || 
                this.lastUpdateTime.toLocaleTimeString() : 
                'Never';
            
            timeElements.forEach(element => {
                element.textContent = timeString;
            });
            
        } catch (error) {
            console.error('❌ Failed to update refresh time:', error);
        }
    }

    /**
     * Show error notification
     */
    showErrorNotification(message) {
        try {
            // Try to use app's notification system
            if (this.app.showError) {
                this.app.showError(message);
            } else {
                // Fallback to console
                console.error('Dashboard Error:', message);
            }
            
        } catch (error) {
            console.error('❌ Failed to show error notification:', error);
        }
    }

    // Error Handling

    /**
     * Handle dashboard errors
     */
    handleError(context, error) {
        console.error(`❌ Dashboard Controller Error [${context}]:`, error);
        
        this.state.lastError = {
            context,
            error: error.message || error,
            timestamp: new Date()
        };
        
        // Show user-friendly error message
        this.showErrorNotification(`${context}: ${error.message || 'Unknown error'}`);
    }

    // Public API Methods

    /**
     * Get current dashboard state
     */
    getState() {
        return {
            ...this.state,
            isInitialized: this.isInitialized,
            isRefreshing: this.isRefreshing,
            lastUpdateTime: this.lastUpdateTime,
            config: this.config
        };
    }

    /**
     * Toggle auto-refresh
     */
    toggleAutoRefresh() {
        if (this.refreshInterval) {
            this.stopAutoRefresh();
            this.config.enableAutoRefresh = false;
        } else {
            this.startAutoRefresh();
            this.config.enableAutoRefresh = true;
        }
        
        console.log(`🔄 Auto-refresh ${this.config.enableAutoRefresh ? 'enabled' : 'disabled'}`);
    }

    /**
     * Force refresh all data
     */
    forceRefresh() {
        console.log('🔄 Force refresh requested');
        return this.refreshAll();
    }

    /**
     * Cleanup resources
     */
    destroy() {
        try {
            console.log('🧹 Cleaning up Dashboard Controller...');
            
            // Stop auto-refresh
            this.stopAutoRefresh();
            
            // Remove event listeners would go here if we tracked them
            // For now, we rely on the app lifecycle
            
            // Clear references
            this.components = {};
            this.state = {
                stats: null,
                tokens: [],
                alerts: [],
                isOnline: false,
                lastError: null
            };
            
            this.isInitialized = false;
            
            console.log('✅ Dashboard Controller cleaned up');
            
        } catch (error) {
            console.error('❌ Failed to cleanup Dashboard Controller:', error);
        }
    }
}

// Export for global use
window.DashboardController = DashboardController;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardController;
}

console.log('🎛️ Dashboard Controller module loaded successfully');