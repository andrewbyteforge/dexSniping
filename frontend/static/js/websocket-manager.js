/**
 * WebSocket Manager Module
 * File: frontend/static/js/websocket-manager.js
 * 
 * Handles WebSocket connections for real-time updates in DEX Sniper Pro.
 * Features auto-reconnection, message queuing, event handling, and connection management.
 */

class WebSocketManager extends EventTarget {
    constructor(url) {
        super();
        this.url = url;
        this.socket = null;
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.heartbeatInterval = 30000; // 30 seconds
        this.messageQueue = [];
        this.subscriptions = new Map();
        
        // Performance monitoring
        this.stats = {
            totalConnections: 0,
            totalReconnections: 0,
            messagesReceived: 0,
            messagesSent: 0,
            lastConnectedAt: null,
            lastDisconnectedAt: null,
            connectionDuration: 0
        };
        
        // Heartbeat management
        this.heartbeatTimer = null;
        this.lastHeartbeat = null;
        
        console.log('🔌 WebSocketManager initialized for URL:', url);
    }

    /**
     * Connect to WebSocket server
     */
    async connect() {
        if (this.isConnected || this.isConnecting) {
            console.warn('⚠️ WebSocket already connected or connecting');
            return;
        }

        this.isConnecting = true;
        console.log('🔄 Connecting to WebSocket...');

        try {
            this.socket = new WebSocket(this.url);
            this.setupEventHandlers();
            
            // Return a promise that resolves when connected
            return new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('WebSocket connection timeout'));
                }, 10000); // 10 second timeout

                this.socket.onopen = () => {
                    clearTimeout(timeout);
                    resolve();
                };

                this.socket.onerror = (error) => {
                    clearTimeout(timeout);
                    reject(error);
                };
            });

        } catch (error) {
            this.isConnecting = false;
            console.error('❌ WebSocket connection failed:', error);
            throw error;
        }
    }

    /**
     * Setup WebSocket event handlers
     */
    setupEventHandlers() {
        this.socket.onopen = (event) => {
            console.log('✅ WebSocket connected successfully');
            this.handleConnectionOpen(event);
        };

        this.socket.onclose = (event) => {
            console.log('🔌 WebSocket connection closed:', event.code, event.reason);
            this.handleConnectionClose(event);
        };

        this.socket.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
            this.handleConnectionError(error);
        };

        this.socket.onmessage = (event) => {
            this.handleMessage(event);
        };
    }

    /**
     * Handle connection open
     */
    handleConnectionOpen(event) {
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000; // Reset delay
        this.stats.totalConnections++;
        this.stats.lastConnectedAt = new Date();
        
        // Update performance monitor
        if (window.PERFORMANCE_MONITOR) {
            window.PERFORMANCE_MONITOR.webSocketReconnects = this.stats.totalReconnections;
        }

        // Start heartbeat
        this.startHeartbeat();

        // Process queued messages
        this.processMessageQueue();

        // Emit connect event
        this.dispatchEvent(new CustomEvent('connect', { detail: event }));
        this.emit('connect', event);

        console.log('🎉 WebSocket ready for real-time updates');
    }

    /**
     * Handle connection close
     */
    handleConnectionClose(event) {
        this.isConnected = false;
        this.isConnecting = false;
        this.stats.lastDisconnectedAt = new Date();
        
        if (this.stats.lastConnectedAt) {
            this.stats.connectionDuration += Date.now() - this.stats.lastConnectedAt.getTime();
        }

        // Stop heartbeat
        this.stopHeartbeat();

        // Emit disconnect event
        this.dispatchEvent(new CustomEvent('disconnect', { detail: event }));
        this.emit('disconnect', event);

        // Auto-reconnect if not intentional close
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
        } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached. Giving up.');
            this.emit('reconnect:failed');
        }
    }

    /**
     * Handle connection error
     */
    handleConnectionError(error) {
        console.error('❌ WebSocket error occurred:', error);
        this.emit('error', error);
    }

    /**
     * Handle incoming messages
     */
    handleMessage(event) {
        this.stats.messagesReceived++;
        
        try {
            const data = JSON.parse(event.data);
            console.log('📨 WebSocket message received:', data.type || 'unknown');
            
            // Handle different message types
            switch (data.type) {
                case 'pong':
                    this.handlePongMessage(data);
                    break;
                case 'stats_update':
                    this.emit('stats_update', data.data);
                    break;
                case 'token_discovery':
                    this.emit('token_discovery', data.data);
                    break;
                case 'live_alert':
                    this.emit('live_alert', data.data);
                    break;
                case 'connection_established':
                    console.log('🎯 Server acknowledged connection:', data.message);
                    break;
                default:
                    console.warn('⚠️ Unknown message type:', data.type);
                    this.emit('message', data);
            }

            // Emit generic message event
            this.dispatchEvent(new CustomEvent('message', { detail: data }));

        } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error);
            this.emit('parse_error', { error, rawData: event.data });
        }
    }

    /**
     * Send message to server
     */
    send(data) {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        
        if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(message);
            this.stats.messagesSent++;
            console.log('📤 WebSocket message sent:', data.type || 'unknown');
        } else {
            // Queue message for later sending
            this.messageQueue.push(message);
            console.log('📬 Message queued (not connected):', data.type || 'unknown');
        }
    }

    /**
     * Process queued messages
     */
    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const message = this.messageQueue.shift();
            this.socket.send(message);
            this.stats.messagesSent++;
        }
        
        if (this.messageQueue.length === 0) {
            console.log('✅ All queued messages processed');
        }
    }

    /**
     * Start heartbeat mechanism
     */
    startHeartbeat() {
        this.stopHeartbeat(); // Clear any existing timer
        
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected) {
                this.sendHeartbeat();
            }
        }, this.heartbeatInterval);
        
        console.log('💓 Heartbeat started');
    }

    /**
     * Stop heartbeat mechanism
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Send heartbeat ping
     */
    sendHeartbeat() {
        this.lastHeartbeat = Date.now();
        this.send({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Handle pong response
     */
    handlePongMessage(data) {
        if (this.lastHeartbeat) {
            const latency = Date.now() - this.lastHeartbeat;
            console.log(`💓 Heartbeat latency: ${latency}ms`);
            this.emit('heartbeat', { latency });
        }
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        this.reconnectAttempts++;
        this.stats.totalReconnections++;
        
        console.log(`🔄 Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectDelay}ms`);
        
        setTimeout(() => {
            if (!this.isConnected && !this.isConnecting) {
                this.connect().catch(error => {
                    console.error('❌ Reconnection failed:', error);
                    
                    // Exponential backoff
                    this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
                });
            }
        }, this.reconnectDelay);
    }

    /**
     * Disconnect from WebSocket
     */
    disconnect() {
        console.log('🔌 Disconnecting WebSocket...');
        
        this.stopHeartbeat();
        
        if (this.socket) {
            this.socket.close(1000, 'Client disconnect');
            this.socket = null;
        }
        
        this.isConnected = false;
        this.isConnecting = false;
    }

    /**
     * Request stats update from server
     */
    requestStatsUpdate() {
        this.send({
            type: 'request_update',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Subscribe to specific event types
     */
    subscribe(eventType, callback) {
        if (!this.subscriptions.has(eventType)) {
            this.subscriptions.set(eventType, new Set());
        }
        
        this.subscriptions.get(eventType).add(callback);
        this.addEventListener(eventType, callback);
        
        console.log(`📡 Subscribed to ${eventType} events`);
    }

    /**
     * Unsubscribe from specific event types
     */
    unsubscribe(eventType, callback) {
        if (this.subscriptions.has(eventType)) {
            this.subscriptions.get(eventType).delete(callback);
            this.removeEventListener(eventType, callback);
        }
    }

    /**
     * Emit events to subscribers
     */
    emit(eventType, data = null) {
        // Dispatch custom event
        this.dispatchEvent(new CustomEvent(eventType, { detail: data }));
        
        // Call direct subscribers
        if (this.subscriptions.has(eventType)) {
            this.subscriptions.get(eventType).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`❌ Error in ${eventType} callback:`, error);
                }
            });
        }
    }

    /**
     * Get connection status
     */
    getStatus() {
        return {
            isConnected: this.isConnected,
            isConnecting: this.isConnecting,
            reconnectAttempts: this.reconnectAttempts,
            readyState: this.socket ? this.socket.readyState : null,
            url: this.url
        };
    }

    /**
     * Get performance statistics
     */
    getStats() {
        return {
            ...this.stats,
            queuedMessages: this.messageQueue.length,
            subscriptions: Object.fromEntries(
                Array.from(this.subscriptions.entries()).map(([key, value]) => [key, value.size])
            )
        };
    }

    /**
     * Test connection by sending a ping
     */
    testConnection() {
        if (this.isConnected) {
            this.sendHeartbeat();
            return true;
        } else {
            console.warn('⚠️ Cannot test connection - not connected');
            return false;
        }
    }

    /**
     * Reset connection statistics
     */
    resetStats() {
        this.stats = {
            totalConnections: 0,
            totalReconnections: 0,
            messagesReceived: 0,
            messagesSent: 0,
            lastConnectedAt: null,
            lastDisconnectedAt: null,
            connectionDuration: 0
        };
        console.log('📊 WebSocket statistics reset');
    }

    /**
     * Force reconnection
     */
    forceReconnect() {
        console.log('🔄 Forcing WebSocket reconnection...');
        
        if (this.socket) {
            this.socket.close();
        }
        
        // Reset connection state
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        
        // Attempt reconnection
        this.connect().catch(error => {
            console.error('❌ Forced reconnection failed:', error);
        });
    }

    /**
     * Enable debug mode with verbose logging
     */
    enableDebug() {
        this.debugMode = true;
        console.log('🔧 WebSocket debug mode enabled');
        
        // Log all events
        ['connect', 'disconnect', 'message', 'error'].forEach(eventType => {
            this.addEventListener(eventType, (event) => {
                console.log(`🐛 WebSocket Debug [${eventType}]:`, event.detail);
            });
        });
    }

    /**
     * Get WebSocket connection quality metrics
     */
    getConnectionQuality() {
        const now = Date.now();
        const uptime = this.stats.lastConnectedAt ? now - this.stats.lastConnectedAt.getTime() : 0;
        const totalDuration = this.stats.connectionDuration + uptime;
        const reliability = this.stats.totalConnections > 0 ? 
            (totalDuration / (this.stats.totalConnections * 60000)) : 0; // Average minutes per connection
        
        return {
            reliability: Math.min(reliability, 1),
            uptime: uptime,
            totalDuration: totalDuration,
            reconnectRate: this.stats.totalReconnections / Math.max(this.stats.totalConnections, 1),
            messageSuccessRate: this.stats.messagesSent > 0 ? 
                this.stats.messagesReceived / this.stats.messagesSent : 0
        };
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketManager;
}

// Make available globally
window.WebSocketManager = WebSocketManager;