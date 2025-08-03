/**
 * WebSocket Manager Module - UPDATED & FIXED
 * File: frontend/static/js/websocket-manager.js
 * 
 * Handles WebSocket connections for real-time updates in DEX Sniper Pro.
 * Features auto-reconnection, message queuing, event handling, and connection management.
 * FIXED: Connection URL construction, error handling, and fallback mechanisms
 */

class WebSocketManager extends EventTarget {
    constructor(url) {
        super();
        this.baseUrl = url;
        this.socket = null;
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10; // ✅ INCREASED from 5 to 10
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.heartbeatInterval = 30000; // 30 seconds
        this.messageQueue = [];
        this.subscriptions = new Map();
        
        // ✅ ADDED: Multiple connection management
        this.connections = new Map();
        this.reconnectTimers = new Map();
        
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
     * UPDATED: Connect to WebSocket server with better URL handling
     */
    async connect(endpoint = '', callbacks = {}) {
        // ✅ FIXED: Better URL construction
        let wsUrl;
        if (endpoint) {
            // Handle specific endpoint connections
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            
            if (endpoint.startsWith('/')) {
                wsUrl = `${protocol}//${host}${endpoint}`;
            } else {
                wsUrl = `${protocol}//${host}/ws/${endpoint}`;
            }
        } else {
            // Use base URL
            wsUrl = this.baseUrl;
        }

        const connectionKey = endpoint || 'default';

        if (this.connections.has(connectionKey)) {
            const existing = this.connections.get(connectionKey);
            if (existing.isConnected || existing.isConnecting) {
                console.warn(`⚠️ WebSocket already connected or connecting to ${endpoint}`);
                return existing.socket;
            }
        }

        console.log(`🔄 Connecting to WebSocket: ${wsUrl}`);

        try {
            const connectionInfo = {
                socket: null,
                isConnected: false,
                isConnecting: true,
                reconnectAttempts: 0,
                callbacks: callbacks,
                url: wsUrl
            };

            this.connections.set(connectionKey, connectionInfo);

            const socket = new WebSocket(wsUrl);
            connectionInfo.socket = socket;
            
            this.setupEventHandlers(socket, connectionKey, callbacks);
            
            // Return a promise that resolves when connected
            return new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    connectionInfo.isConnecting = false;
                    reject(new Error(`WebSocket connection timeout for ${endpoint}`));
                }, 10000); // 10 second timeout

                const originalOnOpen = socket.onopen;
                socket.onopen = (event) => {
                    clearTimeout(timeout);
                    if (originalOnOpen) originalOnOpen(event);
                    resolve(socket);
                };

                const originalOnError = socket.onerror;
                socket.onerror = (error) => {
                    clearTimeout(timeout);
                    connectionInfo.isConnecting = false;
                    if (originalOnError) originalOnError(error);
                    reject(error);
                };
            });

        } catch (error) {
            const connectionInfo = this.connections.get(connectionKey);
            if (connectionInfo) {
                connectionInfo.isConnecting = false;
            }
            console.error(`❌ WebSocket connection failed for ${endpoint}:`, error);
            
            // ✅ ADDED: Schedule reconnection on failure
            this.scheduleReconnect(connectionKey, callbacks);
            throw error;
        }
    }

    /**
     * UPDATED: Setup WebSocket event handlers with connection key tracking
     */
    setupEventHandlers(socket, connectionKey, callbacks = {}) {
        const connectionInfo = this.connections.get(connectionKey);

        socket.onopen = (event) => {
            console.log(`✅ WebSocket connected successfully: ${connectionKey}`);
            this.handleConnectionOpen(event, connectionKey);
            if (callbacks.onOpen) callbacks.onOpen(event);
        };

        socket.onclose = (event) => {
            console.log(`🔌 WebSocket connection closed: ${connectionKey} (${event.code}) ${event.reason || ''}`);
            this.handleConnectionClose(event, connectionKey);
            if (callbacks.onClose) callbacks.onClose(event);
        };

        socket.onerror = (error) => {
            console.error(`❌ WebSocket error for ${connectionKey}:`, error);
            this.handleConnectionError(error, connectionKey);
            if (callbacks.onError) callbacks.onError(error);
        };

        socket.onmessage = (event) => {
            this.handleMessage(event, connectionKey);
            if (callbacks.onMessage) callbacks.onMessage(event);
        };
    }

    /**
     * UPDATED: Handle connection open with connection key
     */
    handleConnectionOpen(event, connectionKey) {
        const connectionInfo = this.connections.get(connectionKey);
        if (connectionInfo) {
            connectionInfo.isConnected = true;
            connectionInfo.isConnecting = false;
            connectionInfo.reconnectAttempts = 0;
        }

        // Update legacy properties for backward compatibility
        if (connectionKey === 'default') {
            this.isConnected = true;
            this.isConnecting = false;
            this.socket = connectionInfo?.socket;
        }

        this.reconnectDelay = 1000; // Reset delay
        this.stats.totalConnections++;
        this.stats.lastConnectedAt = new Date();
        
        // Clear any pending reconnect timer
        if (this.reconnectTimers.has(connectionKey)) {
            clearTimeout(this.reconnectTimers.get(connectionKey));
            this.reconnectTimers.delete(connectionKey);
        }
        
        // Update performance monitor
        if (window.PERFORMANCE_MONITOR) {
            window.PERFORMANCE_MONITOR.webSocketReconnects = this.stats.totalReconnections;
        }

        // Start heartbeat for default connection
        if (connectionKey === 'default') {
            this.startHeartbeat();
            this.processMessageQueue();
        }

        // Emit connect event
        this.dispatchEvent(new CustomEvent('connect', { detail: { event, connectionKey } }));
        this.emit('connect', { event, connectionKey });

        console.log(`🎉 WebSocket ready for real-time updates: ${connectionKey}`);
    }

    /**
     * UPDATED: Handle connection close with connection key
     */
    handleConnectionClose(event, connectionKey) {
        const connectionInfo = this.connections.get(connectionKey);
        if (connectionInfo) {
            connectionInfo.isConnected = false;
            connectionInfo.isConnecting = false;
        }

        // Update legacy properties for backward compatibility
        if (connectionKey === 'default') {
            this.isConnected = false;
            this.isConnecting = false;
        }

        this.stats.lastDisconnectedAt = new Date();
        
        if (this.stats.lastConnectedAt) {
            this.stats.connectionDuration += Date.now() - this.stats.lastConnectedAt.getTime();
        }

        // Stop heartbeat for default connection
        if (connectionKey === 'default') {
            this.stopHeartbeat();
        }

        // Emit disconnect event
        this.dispatchEvent(new CustomEvent('disconnect', { detail: { event, connectionKey } }));
        this.emit('disconnect', { event, connectionKey });

        // ✅ IMPROVED: Auto-reconnect logic with better conditions
        const shouldReconnect = event.code !== 1000 && // Not normal closure
                               event.code !== 1001 && // Not going away
                               connectionInfo && 
                               connectionInfo.reconnectAttempts < this.maxReconnectAttempts;

        if (shouldReconnect) {
            console.log(`🔄 Scheduling reconnect for ${connectionKey} (attempt ${connectionInfo.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
            this.scheduleReconnect(connectionKey, connectionInfo.callbacks);
        } else if (connectionInfo && connectionInfo.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error(`❌ Max reconnection attempts reached for ${connectionKey}. Giving up.`);
            this.emit('reconnect:failed', { connectionKey });
        }
    }

    /**
     * UPDATED: Handle connection error with connection key
     */
    handleConnectionError(error, connectionKey) {
        console.error(`❌ WebSocket error occurred for ${connectionKey}:`, error);
        this.emit('error', { error, connectionKey });
    }

    /**
     * UPDATED: Handle incoming messages with connection key
     */
    handleMessage(event, connectionKey) {
        this.stats.messagesReceived++;
        
        try {
            const data = JSON.parse(event.data);
            console.log(`📨 WebSocket message received from ${connectionKey}:`, data.type || 'unknown');
            
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
                case 'price_update':
                    this.emit('price_update', data.data);
                    break;
                case 'connection_established':
                    console.log(`🎯 Server acknowledged connection for ${connectionKey}:`, data.message);
                    break;
                default:
                    console.log(`📨 Unknown message type from ${connectionKey}:`, data.type);
                    this.emit('message', data);
            }

            // Emit generic message event
            this.dispatchEvent(new CustomEvent('message', { detail: { data, connectionKey } }));

        } catch (error) {
            console.error(`❌ Failed to parse WebSocket message from ${connectionKey}:`, error);
            this.emit('parse_error', { error, rawData: event.data, connectionKey });
        }
    }

    /**
     * ADDED: Schedule reconnection with exponential backoff
     */
    scheduleReconnect(connectionKey, callbacks = {}) {
        const connectionInfo = this.connections.get(connectionKey);
        if (!connectionInfo) return;

        connectionInfo.reconnectAttempts++;
        this.stats.totalReconnections++;
        
        const delay = Math.min(
            this.reconnectDelay * Math.pow(2, connectionInfo.reconnectAttempts - 1),
            this.maxReconnectDelay
        );
        
        console.log(`🔄 Scheduling reconnection for ${connectionKey} in ${delay}ms (attempt ${connectionInfo.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        const timer = setTimeout(async () => {
            this.reconnectTimers.delete(connectionKey);
            
            if (connectionInfo && !connectionInfo.isConnected && !connectionInfo.isConnecting) {
                try {
                    await this.connect(connectionKey === 'default' ? '' : connectionKey, callbacks);
                } catch (error) {
                    console.error(`❌ Reconnection failed for ${connectionKey}:`, error);
                }
            }
        }, delay);
        
        this.reconnectTimers.set(connectionKey, timer);
    }

    /**
     * UPDATED: Send message to specific connection or default
     */
    send(data, connectionKey = 'default') {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        const connectionInfo = this.connections.get(connectionKey);
        
        if (connectionInfo && connectionInfo.isConnected && 
            connectionInfo.socket.readyState === WebSocket.OPEN) {
            connectionInfo.socket.send(message);
            this.stats.messagesSent++;
            console.log(`📤 WebSocket message sent to ${connectionKey}:`, data.type || 'unknown');
            return true;
        } else {
            // Queue message for later sending (only for default connection)
            if (connectionKey === 'default') {
                this.messageQueue.push(message);
                console.log('📬 Message queued (not connected):', data.type || 'unknown');
            } else {
                console.warn(`⚠️ Cannot send message to ${connectionKey}: not connected`);
            }
            return false;
        }
    }

    /**
     * Process queued messages (unchanged)
     */
    processMessageQueue() {
        const defaultConnection = this.connections.get('default');
        
        while (this.messageQueue.length > 0 && 
               defaultConnection && defaultConnection.isConnected) {
            const message = this.messageQueue.shift();
            defaultConnection.socket.send(message);
            this.stats.messagesSent++;
        }
        
        if (this.messageQueue.length === 0) {
            console.log('✅ All queued messages processed');
        }
    }

    /**
     * Start heartbeat mechanism (unchanged)
     */
    startHeartbeat() {
        this.stopHeartbeat(); // Clear any existing timer
        
        this.heartbeatTimer = setInterval(() => {
            const defaultConnection = this.connections.get('default');
            if (defaultConnection && defaultConnection.isConnected) {
                this.sendHeartbeat();
            }
        }, this.heartbeatInterval);
        
        console.log('💓 Heartbeat started');
    }

    /**
     * Stop heartbeat mechanism (unchanged)
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Send heartbeat ping (unchanged)
     */
    sendHeartbeat() {
        this.lastHeartbeat = Date.now();
        this.send({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Handle pong response (unchanged)
     */
    handlePongMessage(data) {
        if (this.lastHeartbeat) {
            const latency = Date.now() - this.lastHeartbeat;
            console.log(`💓 Heartbeat latency: ${latency}ms`);
            this.emit('heartbeat', { latency });
        }
    }

    /**
     * UPDATED: Disconnect from WebSocket(s)
     */
    disconnect(connectionKey = null) {
        if (connectionKey) {
            // Disconnect specific connection
            const connectionInfo = this.connections.get(connectionKey);
            if (connectionInfo && connectionInfo.socket) {
                console.log(`🔌 Disconnecting WebSocket: ${connectionKey}`);
                connectionInfo.socket.close(1000, 'Client disconnect');
                this.connections.delete(connectionKey);
                
                // Clear reconnect timer
                if (this.reconnectTimers.has(connectionKey)) {
                    clearTimeout(this.reconnectTimers.get(connectionKey));
                    this.reconnectTimers.delete(connectionKey);
                }
            }
        } else {
            // Disconnect all connections
            console.log('🔌 Disconnecting all WebSocket connections...');
            
            this.stopHeartbeat();
            
            this.connections.forEach((connectionInfo, key) => {
                if (connectionInfo.socket) {
                    connectionInfo.socket.close(1000, 'Client disconnect');
                }
            });
            
            this.connections.clear();
            
            // Clear all reconnect timers
            this.reconnectTimers.forEach(timer => clearTimeout(timer));
            this.reconnectTimers.clear();
            
            // Update legacy properties
            this.socket = null;
            this.isConnected = false;
            this.isConnecting = false;
        }
    }

    /**
     * Request stats update from server (unchanged)
     */
    requestStatsUpdate() {
        this.send({
            type: 'request_update',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Subscribe to specific event types (unchanged)
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
     * Unsubscribe from specific event types (unchanged)
     */
    unsubscribe(eventType, callback) {
        if (this.subscriptions.has(eventType)) {
            this.subscriptions.get(eventType).delete(callback);
            this.removeEventListener(eventType, callback);
        }
    }

    /**
     * Emit events to subscribers (unchanged)
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
     * UPDATED: Get connection status
     */
    getStatus(connectionKey = 'default') {
        const connectionInfo = this.connections.get(connectionKey);
        
        if (connectionInfo) {
            return {
                isConnected: connectionInfo.isConnected,
                isConnecting: connectionInfo.isConnecting,
                reconnectAttempts: connectionInfo.reconnectAttempts,
                readyState: connectionInfo.socket ? connectionInfo.socket.readyState : null,
                url: connectionInfo.url
            };
        }
        
        return {
            isConnected: false,
            isConnecting: false,
            reconnectAttempts: 0,
            readyState: null,
            url: null
        };
    }

    /**
     * UPDATED: Get performance statistics
     */
    getStats() {
        return {
            ...this.stats,
            queuedMessages: this.messageQueue.length,
            activeConnections: this.connections.size,
            connectionKeys: Array.from(this.connections.keys()),
            subscriptions: Object.fromEntries(
                Array.from(this.subscriptions.entries()).map(([key, value]) => [key, value.size])
            )
        };
    }

    /**
     * Test connection by sending a ping (updated)
     */
    testConnection(connectionKey = 'default') {
        const connectionInfo = this.connections.get(connectionKey);
        
        if (connectionInfo && connectionInfo.isConnected) {
            if (connectionKey === 'default') {
                this.sendHeartbeat();
            } else {
                this.send({ type: 'ping', timestamp: new Date().toISOString() }, connectionKey);
            }
            return true;
        } else {
            console.warn(`⚠️ Cannot test connection ${connectionKey} - not connected`);
            return false;
        }
    }

    /**
     * Reset connection statistics (unchanged)
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
     * UPDATED: Force reconnection
     */
    forceReconnect(connectionKey = 'default') {
        console.log(`🔄 Forcing WebSocket reconnection for: ${connectionKey}`);
        
        const connectionInfo = this.connections.get(connectionKey);
        if (connectionInfo) {
            const callbacks = connectionInfo.callbacks;
            
            // Close existing connection
            if (connectionInfo.socket) {
                connectionInfo.socket.close();
            }
            
            // Reset connection state
            connectionInfo.isConnected = false;
            connectionInfo.isConnecting = false;
            connectionInfo.reconnectAttempts = 0;
            
            // Attempt reconnection
            this.connect(connectionKey === 'default' ? '' : connectionKey, callbacks)
                .catch(error => {
                    console.error(`❌ Forced reconnection failed for ${connectionKey}:`, error);
                });
        }
    }

    /**
     * Enable debug mode with verbose logging (unchanged)
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
     * Get WebSocket connection quality metrics (unchanged)
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