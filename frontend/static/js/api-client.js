/**
 * API Client Module
 * File: frontend/static/js/api-client.js
 * 
 * Centralized API communication layer for DEX Sniper Pro.
 * Handles all HTTP requests, error management, caching, and response processing.
 */

class ApiClient extends EventTarget {
    constructor(baseUrl = '/api/v1') {
        super();
        this.baseUrl = baseUrl;
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30 seconds
        this.requestCount = 0;
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second
        
        // Performance monitoring
        this.performance = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            averageResponseTime: 0,
            cacheHits: 0
        };
        
        console.log('✅ ApiClient initialized with base URL:', baseUrl);
    }

    /**
     * Perform GET request
     */
    async get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }

    /**
     * Perform POST request
     */
    async post(endpoint, data = null, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    /**
     * Perform PUT request
     */
    async put(endpoint, data = null, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    /**
     * Perform DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    /**
     * Main request method with error handling, caching, and retries
     */
    async request(method, endpoint, data = null, options = {}) {
        const startTime = performance.now();
        const url = `${this.baseUrl}${endpoint}`;
        const cacheKey = `${method}:${endpoint}`;
        
        // Increment request counter
        this.requestCount++;
        this.performance.totalRequests++;
        
        // Update performance monitor
        if (window.PERFORMANCE_MONITOR) {
            window.PERFORMANCE_MONITOR.apiCalls++;
        }

        // Check cache for GET requests
        if (method === 'GET' && options.cache !== false) {
            const cachedData = this.getFromCache(cacheKey);
            if (cachedData) {
                this.performance.cacheHits++;
                console.log(`📋 Cache hit for ${endpoint}`);
                return cachedData;
            }
        }

        // Prepare request options
        const requestOptions = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            },
            ...options.fetchOptions
        };

        // Add body for POST/PUT requests
        if (data && (method === 'POST' || method === 'PUT')) {
            requestOptions.body = JSON.stringify(data);
        }

        // Add query parameters for GET requests
        if (data && method === 'GET') {
            const queryParams = new URLSearchParams(data);
            const separator = url.includes('?') ? '&' : '?';
            url += separator + queryParams.toString();
        }

        // Perform request with retry logic
        let lastError;
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                console.log(`🔄 API ${method} ${endpoint} (attempt ${attempt}/${this.retryAttempts})`);
                
                const response = await fetch(url, requestOptions);
                const responseTime = performance.now() - startTime;
                
                // Update average response time
                this.updateAverageResponseTime(responseTime);
                
                if (!response.ok) {
                    throw new ApiError(`HTTP ${response.status}: ${response.statusText}`, response.status, response);
                }

                const responseData = await this.parseResponse(response);
                
                // Cache successful GET requests
                if (method === 'GET' && options.cache !== false) {
                    this.setCache(cacheKey, responseData);
                }

                // Update performance stats
                this.performance.successfulRequests++;
                
                console.log(`✅ API ${method} ${endpoint} completed in ${responseTime.toFixed(2)}ms`);
                
                // Emit success event
                this.dispatchEvent(new CustomEvent('request:success', {
                    detail: { method, endpoint, responseTime, data: responseData }
                }));

                return responseData;

            } catch (error) {
                lastError = error;
                console.warn(`❌ API ${method} ${endpoint} failed (attempt ${attempt}):`, error.message);
                
                // Don't retry on client errors (4xx)
                if (error.status >= 400 && error.status < 500) {
                    break;
                }
                
                // Wait before retrying (except on last attempt)
                if (attempt < this.retryAttempts) {
                    await this.delay(this.retryDelay * attempt);
                }
            }
        }

        // All attempts failed
        this.performance.failedRequests++;
        
        // Emit error event
        this.dispatchEvent(new CustomEvent('request:error', {
            detail: { method, endpoint, error: lastError }
        }));

        // Throw the last error
        throw lastError;
    }

    /**
     * Parse response based on content type
     */
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else if (contentType && contentType.includes('text/')) {
            return await response.text();
        } else {
            return response;
        }
    }

    /**
     * Cache management
     */
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        
        // Remove expired cache entry
        if (cached) {
            this.cache.delete(key);
        }
        
        return null;
    }

    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
        
        // Clean up old cache entries (keep last 100)
        if (this.cache.size > 100) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
        }
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('🗑️ API cache cleared');
    }

    /**
     * Update average response time
     */
    updateAverageResponseTime(responseTime) {
        const totalRequests = this.performance.successfulRequests;
        const currentAverage = this.performance.averageResponseTime;
        
        this.performance.averageResponseTime = 
            (currentAverage * (totalRequests - 1) + responseTime) / totalRequests;
    }

    /**
     * Utility delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get performance statistics
     */
    getPerformanceStats() {
        return {
            ...this.performance,
            cacheSize: this.cache.size,
            cacheHitRate: this.performance.cacheHits / this.performance.totalRequests || 0
        };
    }

    /**
     * Health check endpoint
     */
    async healthCheck() {
        try {
            const response = await this.get('/health', { cache: false });
            return response.status === 'healthy';
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    /**
     * Dashboard-specific API methods
     */

    // Get dashboard statistics
    async getDashboardStats() {
        return this.get('/dashboard/stats');
    }

    // Get live tokens with filtering
    async getLiveTokens(filters = {}) {
        const queryParams = new URLSearchParams();
        
        if (filters.network) queryParams.append('network', filters.network);
        if (filters.risk_level) queryParams.append('risk_level', filters.risk_level);
        if (filters.min_liquidity) queryParams.append('min_liquidity', filters.min_liquidity);
        if (filters.limit) queryParams.append('limit', filters.limit);
        
        const endpoint = `/dashboard/tokens/live?${queryParams.toString()}`;
        return this.get(endpoint);
    }

    // Token discovery
    async discoverTokens(options = {}) {
        const queryParams = new URLSearchParams();
        
        if (options.networks) {
            options.networks.forEach(network => queryParams.append('networks', network));
        }
        if (options.limit) queryParams.append('limit', options.limit);
        if (options.min_liquidity) queryParams.append('min_liquidity', options.min_liquidity);
        
        const endpoint = `/tokens/discover?${queryParams.toString()}`;
        return this.get(endpoint);
    }

    // Analyze specific token
    async analyzeToken(address, network = 'Ethereum') {
        return this.post('/tokens/analyze', { address, network });
    }

    // Get token information
    async getTokenInfo(network, address) {
        return this.get(`/tokens/${network}/${address}`);
    }

    // Send alert
    async sendAlert(alertType, title, message, severity = 'info', tokenAddress = null) {
        return this.post('/dashboard/alerts/send', {
            alert_type: alertType,
            title,
            message,
            severity,
            token_address: tokenAddress
        });
    }

    // Get token statistics
    async getTokenStats() {
        return this.get('/tokens/stats');
    }

    /**
     * Batch request utility
     */
    async batchRequest(requests) {
        const startTime = performance.now();
        console.log(`🔄 Executing batch request with ${requests.length} requests`);
        
        try {
            const promises = requests.map(({ method, endpoint, data, options }) =>
                this.request(method, endpoint, data, options).catch(error => ({ error }))
            );
            
            const results = await Promise.all(promises);
            const responseTime = performance.now() - startTime;
            
            const successful = results.filter(result => !result.error).length;
            const failed = results.length - successful;
            
            console.log(`✅ Batch request completed: ${successful} successful, ${failed} failed in ${responseTime.toFixed(2)}ms`);
            
            return results;
        } catch (error) {
            console.error('❌ Batch request failed:', error);
            throw error;
        }
    }

    /**
     * Request cancellation support
     */
    createCancellableRequest(method, endpoint, data = null, options = {}) {
        const controller = new AbortController();
        
        const requestPromise = this.request(method, endpoint, data, {
            ...options,
            fetchOptions: {
                ...options.fetchOptions,
                signal: controller.signal
            }
        });
        
        return {
            promise: requestPromise,
            cancel: () => {
                controller.abort();
                console.log(`🚫 Request cancelled: ${method} ${endpoint}`);
            }
        };
    }
}

/**
 * Custom API Error class
 */
class ApiError extends Error {
    constructor(message, status = null, response = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.response = response;
        this.timestamp = new Date().toISOString();
    }

    toJSON() {
        return {
            name: this.name,
            message: this.message,
            status: this.status,
            timestamp: this.timestamp
        };
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiClient, ApiError };
}

// Make available globally
window.ApiClient = ApiClient;
window.ApiError = ApiError;