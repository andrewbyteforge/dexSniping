/**
 * Real-time Price Feed Controller
 * File: frontend/static/js/components/price-feed-controller.js
 * 
 * Manages real-time price updates via WebSocket for professional trading interface.
 * Integrates with chart controller and technical indicators for live updates.
 */

class PriceFeedController {
    constructor() {
        this.websocket = null;
        this.subscriptions = new Map(); // token_address -> subscription details
        this.priceData = new Map(); // token_address -> price history
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.chartController = null;
        
        // Price update callbacks
        this.callbacks = new Map();
        this.globalCallbacks = [];
        
        // Connection status indicators
        this.statusElement = null;
        
        this.init();
        console.log('✅ PriceFeedController initialized');
    }

    /**
     * Initialize price feed system
     */
    async init() {
        try {
            this.statusElement = document.getElementById('price-feed-status');
            this.chartController = window.chartController || new ChartController();
            
            await this.connect();
            this.bindEvents();
            
        } catch (error) {
            console.error('Error initializing PriceFeedController:', error);
        }
    }

    /**
     * Connect to WebSocket price feed
     */
    async connect() {
        try {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                console.log('WebSocket already connected');
                return;
            }

            const wsUrl = this.getWebSocketUrl();
            console.log(`🔌 Connecting to price feed: ${wsUrl}`);
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = this.handleOpen.bind(this);
            this.websocket.onmessage = this.handleMessage.bind(this);
            this.websocket.onerror = this.handleError.bind(this);
            this.websocket.onclose = this.handleClose.bind(this);
            
        } catch (error) {
            console.error('Error connecting to price feed:', error);
            this.updateConnectionStatus('error', 'Connection failed');
        }
    }

    /**
     * Get WebSocket URL
     */
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/price-feed`;
    }

    /**
     * Handle WebSocket connection open
     */
    handleOpen(event) {
        console.log('✅ Price feed WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateConnectionStatus('connected', 'Live price feed active');
        
        // Resubscribe to existing subscriptions
        this.resubscribeAll();
    }

    /**
     * Handle incoming WebSocket messages
     * Method: handleMessage()
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'price_update':
                    this.handlePriceUpdate(data);
                    break;
                case 'bulk_price_update':
                    this.handleBulkPriceUpdate(data);
                    break;
                case 'market_status':
                    this.handleMarketStatus(data);
                    break;
                case 'technical_indicators':
                    this.handleTechnicalIndicators(data);
                    break;
                case 'subscription_confirmed':
                    this.handleSubscriptionConfirmed(data);
                    break;
                case 'error':
                    this.handleServerError(data);
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
            
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    }

    /**
     * Handle single price update
     */
    handlePriceUpdate(data) {
        try {
            const { token_address, price_usd, price_eth, volume_24h, timestamp } = data;
            
            // Store price data
            if (!this.priceData.has(token_address)) {
                this.priceData.set(token_address, []);
            }
            
            const priceHistory = this.priceData.get(token_address);
            priceHistory.push({
                price_usd: parseFloat(price_usd),
                price_eth: parseFloat(price_eth),
                volume_24h: parseFloat(volume_24h),
                timestamp: new Date(timestamp)
            });
            
            // Keep only last 1000 price points
            if (priceHistory.length > 1000) {
                priceHistory.shift();
            }
            
            // Update UI elements
            this.updatePriceDisplays(token_address, data);
            
            // Update charts in real-time
            this.updateChartRealtime(token_address, data);
            
            // Trigger callbacks
            this.triggerCallbacks(token_address, data);
            
            // Update last seen
            this.updateLastSeen();
            
        } catch (error) {
            console.error('Error handling price update:', error);
        }
    }

    /**
     * Handle bulk price updates
     */
    handleBulkPriceUpdate(data) {
        try {
            const { updates } = data;
            
            updates.forEach(update => {
                this.handlePriceUpdate(update);
            });
            
        } catch (error) {
            console.error('Error handling bulk price update:', error);
        }
    }

    /**
     * Handle technical indicators update
     */
    handleTechnicalIndicators(data) {
        try {
            const { token_address, indicators } = data;
            
            // Update chart indicators
            if (this.chartController) {
                this.chartController.updateIndicators(token_address, indicators);
            }
            
            // Update indicator displays
            this.updateIndicatorDisplays(token_address, indicators);
            
        } catch (error) {
            console.error('Error handling technical indicators:', error);
        }
    }

    /**
     * Handle market status updates
     */
    handleMarketStatus(data) {
        try {
            const { status, message, active_pairs } = data;
            
            this.updateConnectionStatus(status, message);
            
            // Update active pairs count
            const pairsElement = document.getElementById('active-pairs-count');
            if (pairsElement) {
                pairsElement.textContent = active_pairs || 0;
            }
            
        } catch (error) {
            console.error('Error handling market status:', error);
        }
    }

    /**
     * Handle subscription confirmation
     */
    handleSubscriptionConfirmed(data) {
        try {
            const { token_address, success, message } = data;
            
            if (success) {
                console.log(`✅ Subscription confirmed for ${token_address}`);
                this.subscriptions.set(token_address, {
                    active: true,
                    confirmed_at: new Date()
                });
            } else {
                console.error(`❌ Subscription failed for ${token_address}: ${message}`);
            }
            
        } catch (error) {
            console.error('Error handling subscription confirmation:', error);
        }
    }

    /**
     * Handle server errors
     */
    handleServerError(data) {
        console.error('Server error:', data.message);
        this.updateConnectionStatus('error', data.message);
    }

    /**
     * Subscribe to price updates for a token
     * Method: subscribeToPriceUpdates()
     */
    subscribeToPriceUpdates(tokenAddress, options = {}) {
        try {
            if (!this.isConnected) {
                console.warn('WebSocket not connected, queuing subscription');
                this.subscriptions.set(tokenAddress, { queued: true, options });
                return;
            }

            const subscriptionMessage = {
                type: 'subscribe',
                token_address: tokenAddress,
                options: {
                    include_technical_indicators: true,
                    update_frequency: options.frequency || 'real-time',
                    include_volume: true,
                    include_market_data: true,
                    ...options
                }
            };

            this.websocket.send(JSON.stringify(subscriptionMessage));
            
            this.subscriptions.set(tokenAddress, {
                active: false, // Will be set to true on confirmation
                subscribed_at: new Date(),
                options
            });

            console.log(`📡 Subscribed to price updates for ${tokenAddress}`);
            
        } catch (error) {
            console.error(`Error subscribing to ${tokenAddress}:`, error);
        }
    }

    /**
     * Unsubscribe from price updates
     */
    unsubscribePriceUpdates(tokenAddress) {
        try {
            if (!this.isConnected) {
                this.subscriptions.delete(tokenAddress);
                return;
            }

            const unsubscribeMessage = {
                type: 'unsubscribe',
                token_address: tokenAddress
            };

            this.websocket.send(JSON.stringify(unsubscribeMessage));
            this.subscriptions.delete(tokenAddress);
            this.priceData.delete(tokenAddress);

            console.log(`📡 Unsubscribed from ${tokenAddress}`);
            
        } catch (error) {
            console.error(`Error unsubscribing from ${tokenAddress}:`, error);
        }
    }

    /**
     * Update chart with real-time data
     * Method: updateChartRealtime()
     */
    updateChartRealtime(tokenAddress, priceData) {
        try {
            if (!this.chartController) return;

            // Format data for chart update
            const chartData = {
                price: parseFloat(priceData.price_usd),
                volume: parseFloat(priceData.volume_24h),
                timestamp: new Date(priceData.timestamp),
                updateIndicators: true,
                prices: this.getPriceHistory(tokenAddress)
            };

            // Update main chart
            this.chartController.updateChartRealtime(tokenAddress, chartData);

        } catch (error) {
            console.error('Error updating chart real-time:', error);
        }
    }

    /**
     * Update price displays in UI
     */
    updatePriceDisplays(tokenAddress, priceData) {
        try {
            // Update price elements
            const priceElements = document.querySelectorAll(`[data-token="${tokenAddress}"][data-field="price"]`);
            priceElements.forEach(element => {
                element.textContent = `$${parseFloat(priceData.price_usd).toFixed(6)}`;
            });

            // Update volume elements
            const volumeElements = document.querySelectorAll(`[data-token="${tokenAddress}"][data-field="volume"]`);
            volumeElements.forEach(element => {
                element.textContent = this.formatVolume(priceData.volume_24h);
            });

            // Update price change indicators
            this.updatePriceChangeIndicators(tokenAddress, priceData);

        } catch (error) {
            console.error('Error updating price displays:', error);
        }
    }

    /**
     * Update price change indicators
     */
    updatePriceChangeIndicators(tokenAddress, priceData) {
        try {
            const priceHistory = this.priceData.get(tokenAddress);
            if (!priceHistory || priceHistory.length < 2) return;

            const currentPrice = parseFloat(priceData.price_usd);
            const previousPrice = priceHistory[priceHistory.length - 2].price_usd;
            const change = ((currentPrice - previousPrice) / previousPrice) * 100;

            const changeElements = document.querySelectorAll(`[data-token="${tokenAddress}"][data-field="change"]`);
            changeElements.forEach(element => {
                element.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
                element.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
            });

        } catch (error) {
            console.error('Error updating price change indicators:', error);
        }
    }

    /**
     * Update technical indicator displays
     */
    updateIndicatorDisplays(tokenAddress, indicators) {
        try {
            // Update RSI
            if (indicators.rsi) {
                const rsiElements = document.querySelectorAll(`[data-token="${tokenAddress}"][data-field="rsi"]`);
                rsiElements.forEach(element => {
                    const rsiValue = indicators.rsi[indicators.rsi.length - 1];
                    element.textContent = rsiValue.toFixed(1);
                    
                    // Add signal classes
                    element.className = `indicator-value ${this.getRSISignalClass(rsiValue)}`;
                });
            }

            // Update MACD
            if (indicators.macd) {
                const macdElements = document.querySelectorAll(`[data-token="${tokenAddress}"][data-field="macd"]`);
                macdElements.forEach(element => {
                    const macdValue = indicators.macd.macd[indicators.macd.macd.length - 1];
                    element.textContent = macdValue.toFixed(4);
                });
            }

        } catch (error) {
            console.error('Error updating indicator displays:', error);
        }
    }

    /**
     * Get RSI signal class for styling
     */
    getRSISignalClass(rsiValue) {
        if (rsiValue <= 30) return 'oversold';
        if (rsiValue >= 70) return 'overbought';
        return 'neutral';
    }

    /**
     * Add price update callback
     */
    addPriceCallback(tokenAddress, callback) {
        if (!this.callbacks.has(tokenAddress)) {
            this.callbacks.set(tokenAddress, []);
        }
        this.callbacks.get(tokenAddress).push(callback);
    }

    /**
     * Add global price update callback
     */
    addGlobalCallback(callback) {
        this.globalCallbacks.push(callback);
    }

    /**
     * Trigger callbacks for price updates
     */
    triggerCallbacks(tokenAddress, priceData) {
        try {
            // Token-specific callbacks
            const tokenCallbacks = this.callbacks.get(tokenAddress);
            if (tokenCallbacks) {
                tokenCallbacks.forEach(callback => {
                    try {
                        callback(tokenAddress, priceData);
                    } catch (error) {
                        console.error('Error in price callback:', error);
                    }
                });
            }

            // Global callbacks
            this.globalCallbacks.forEach(callback => {
                try {
                    callback(tokenAddress, priceData);
                } catch (error) {
                    console.error('Error in global price callback:', error);
                }
            });

        } catch (error) {
            console.error('Error triggering callbacks:', error);
        }
    }

    /**
     * Get price history for a token
     */
    getPriceHistory(tokenAddress) {
        const history = this.priceData.get(tokenAddress);
        return history ? history.map(item => item.price_usd) : [];
    }

    /**
     * Format volume for display
     */
    formatVolume(volume) {
        const num = parseFloat(volume);
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toFixed(2);
    }

    /**
     * Update connection status display
     */
    updateConnectionStatus(status, message) {
        if (this.statusElement) {
            this.statusElement.className = `connection-status status-${status}`;
            this.statusElement.textContent = message;
        }

        // Update status indicator in header
        const statusIndicator = document.querySelector('.price-feed-indicator');
        if (statusIndicator) {
            statusIndicator.className = `price-feed-indicator ${status}`;
        }
    }

    /**
     * Update last seen timestamp
     */
    updateLastSeen() {
        const lastSeenElement = document.getElementById('last-price-update');
        if (lastSeenElement) {
            lastSeenElement.textContent = new Date().toLocaleTimeString();
        }
    }

    /**
     * Resubscribe to all existing subscriptions
     */
    resubscribeAll() {
        try {
            this.subscriptions.forEach((subscription, tokenAddress) => {
                if (subscription.queued || subscription.active) {
                    this.subscribeToPriceUpdates(tokenAddress, subscription.options);
                }
            });
        } catch (error) {
            console.error('Error resubscribing to price feeds:', error);
        }
    }

    /**
     * Handle WebSocket errors
     */
    handleError(event) {
        console.error('WebSocket error:', event);
        this.updateConnectionStatus('error', 'Connection error occurred');
    }

    /**
     * Handle WebSocket close
     */
    handleClose(event) {
        console.log('WebSocket connection closed:', event.code, event.reason);
        this.isConnected = false;
        this.updateConnectionStatus('disconnected', 'Connection lost - attempting to reconnect...');
        
        // Attempt to reconnect
        this.attemptReconnect();
    }

    /**
     * Attempt to reconnect to WebSocket
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus('failed', 'Connection failed - manual refresh required');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Bind event handlers
     */
    bindEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });

        // Handle connection controls
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-price-feed-action]')) {
                this.handleAction(e.target);
            }
        });
    }

    /**
     * Handle price feed actions
     */
    handleAction(element) {
        const action = element.dataset.priceFeedAction;
        
        switch (action) {
            case 'reconnect':
                this.reconnect();
                break;
            case 'pause':
                this.pauseUpdates();
                break;
            case 'resume':
                this.resumeUpdates();
                break;
        }
    }

    /**
     * Manually reconnect
     */
    reconnect() {
        if (this.websocket) {
            this.websocket.close();
        }
        this.reconnectAttempts = 0;
        this.connect();
    }

    /**
     * Pause price updates
     */
    pauseUpdates() {
        if (this.websocket && this.isConnected) {
            this.websocket.send(JSON.stringify({ type: 'pause' }));
        }
    }

    /**
     * Resume price updates
     */
    resumeUpdates() {
        if (this.websocket && this.isConnected) {
            this.websocket.send(JSON.stringify({ type: 'resume' }));
        }
    }

    /**
     * Get connection statistics
     */
    getConnectionStats() {
        return {
            isConnected: this.isConnected,
            subscriptions: this.subscriptions.size,
            reconnectAttempts: this.reconnectAttempts,
            priceDataPoints: Array.from(this.priceData.values()).reduce(
                (total, history) => total + history.length, 
                0
            )
        };
    }

    /**
     * Clean up resources
     */
    destroy() {
        try {
            // Close WebSocket connection
            if (this.websocket) {
                this.websocket.close();
            }

            // Clear all data
            this.subscriptions.clear();
            this.priceData.clear();
            this.callbacks.clear();
            this.globalCallbacks = [];

            console.log('✅ PriceFeedController destroyed');
        } catch (error) {
            console.error('Error destroying PriceFeedController:', error);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PriceFeedController;
} else {
    window.PriceFeedController = PriceFeedController;
}