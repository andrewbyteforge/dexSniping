/**
 * Constants Utility Module
 * File: frontend/static/js/utils/constants.js
 * 
 * Application constants and configuration values for DEX Sniper Pro.
 * Centralized location for all constant values used throughout the application.
 */

// Application Information
window.APP_CONSTANTS = {
    // Application Metadata
    APP_NAME: 'DEX Sniper Pro',
    VERSION: '3.1.0',
    PHASE: '3B',
    BUILD_DATE: '2025-08-03',
    
    // API Configuration
    API: {
        BASE_URL: '/api/v1',
        TIMEOUT: 30000, // 30 seconds
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000, // 1 second
        CACHE_TIMEOUT: 30000, // 30 seconds
        RATE_LIMIT: 100, // requests per minute
    },
    
    // WebSocket Configuration
    WEBSOCKET: {
        URL: `ws://${window.location.host}/api/v1/dashboard/ws`,
        RECONNECT_ATTEMPTS: 5,
        RECONNECT_DELAY: 1000, // 1 second
        MAX_RECONNECT_DELAY: 30000, // 30 seconds
        HEARTBEAT_INTERVAL: 30000, // 30 seconds
        MESSAGE_QUEUE_LIMIT: 100,
    },
    
    // Supported Blockchain Networks
    NETWORKS: {
        ETHEREUM: {
            name: 'Ethereum',
            symbol: 'ETH',
            chainId: 1,
            color: '#627eea',
            blockTime: 12, // seconds
            explorer: 'https://etherscan.io',
            coingeckoId: 'ethereum'
        },
        POLYGON: {
            name: 'Polygon',
            symbol: 'MATIC',
            chainId: 137,
            color: '#8247e5',
            blockTime: 2,
            explorer: 'https://polygonscan.com',
            coingeckoId: 'matic-network'
        },
        BSC: {
            name: 'Binance Smart Chain',
            symbol: 'BNB',
            chainId: 56,
            color: '#f3ba2f',
            blockTime: 3,
            explorer: 'https://bscscan.com',
            coingeckoId: 'binancecoin'
        },
        ARBITRUM: {
            name: 'Arbitrum',
            symbol: 'ARB',
            chainId: 42161,
            color: '#28a0f0',
            blockTime: 1,
            explorer: 'https://arbiscan.io',
            coingeckoId: 'arbitrum'
        },
        OPTIMISM: {
            name: 'Optimism',
            symbol: 'OP',
            chainId: 10,
            color: '#ff0420',
            blockTime: 2,
            explorer: 'https://optimistic.etherscan.io',
            coingeckoId: 'optimism'
        },
        AVALANCHE: {
            name: 'Avalanche',
            symbol: 'AVAX',
            chainId: 43114,
            color: '#e84142',
            blockTime: 2,
            explorer: 'https://snowtrace.io',
            coingeckoId: 'avalanche-2'
        },
        FANTOM: {
            name: 'Fantom',
            symbol: 'FTM',
            chainId: 250,
            color: '#1969ff',
            blockTime: 1,
            explorer: 'https://ftmscan.com',
            coingeckoId: 'fantom'
        },
        SOLANA: {
            name: 'Solana',
            symbol: 'SOL',
            chainId: null, // Solana doesn't use EVM chain IDs
            color: '#9945ff',
            blockTime: 0.4,
            explorer: 'https://solscan.io',
            coingeckoId: 'solana'
        }
    },
    
    // Risk Assessment Levels
    RISK_LEVELS: {
        LOW: {
            value: 'low',
            threshold: 3,
            color: '#28a745',
            backgroundColor: '#d4edda',
            label: 'Low Risk',
            description: 'Generally safe for trading'
        },
        MEDIUM: {
            value: 'medium',
            threshold: 7,
            color: '#ffc107',
            backgroundColor: '#fff3cd',
            label: 'Medium Risk',
            description: 'Exercise caution'
        },
        HIGH: {
            value: 'high',
            threshold: 10,
            color: '#dc3545',
            backgroundColor: '#f8d7da',
            label: 'High Risk',
            description: 'Proceed with extreme caution'
        }
    },
    
    // Refresh Intervals (milliseconds)
    REFRESH_INTERVALS: {
        STATS: 10000,        // 10 seconds
        TOKENS: 30000,       // 30 seconds
        PORTFOLIO: 60000,    // 1 minute
        ALERTS: 5000,        // 5 seconds
        HEALTH_CHECK: 300000, // 5 minutes
        ARBITRAGE: 15000,    // 15 seconds
        PRICES: 5000,        // 5 seconds
    },
    
    // UI Configuration
    UI: {
        SIDEBAR_WIDTH: 280,
        HEADER_HEIGHT: 70,
        MOBILE_BREAKPOINT: 768,
        TABLET_BREAKPOINT: 1024,
        DESKTOP_BREAKPOINT: 1200,
        
        // Animation durations (milliseconds)
        ANIMATION: {
            FAST: 150,
            NORMAL: 300,
            SLOW: 500,
            VERY_SLOW: 1000
        },
        
        // Notification settings
        NOTIFICATIONS: {
            DEFAULT_DURATION: 5000, // 5 seconds
            ERROR_DURATION: 10000,  // 10 seconds
            SUCCESS_DURATION: 3000, // 3 seconds
            MAX_NOTIFICATIONS: 5
        },
        
        // Table pagination
        PAGINATION: {
            DEFAULT_PAGE_SIZE: 20,
            PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
            MAX_PAGE_SIZE: 100
        }
    },
    
    // Trading Configuration
    TRADING: {
        MIN_TRADE_AMOUNT: 0.001,
        MAX_TRADE_AMOUNT: 1000,
        DEFAULT_SLIPPAGE: 0.5, // 0.5%
        MAX_SLIPPAGE: 50, // 50%
        GAS_MULTIPLIER: 1.2,
        
        // Order types
        ORDER_TYPES: {
            MARKET: 'market',
            LIMIT: 'limit',
            STOP_LOSS: 'stop_loss',
            TAKE_PROFIT: 'take_profit'
        },
        
        // Position sizes
        POSITION_SIZES: {
            SMALL: 0.1,
            MEDIUM: 0.25,
            LARGE: 0.5,
            MAX: 1.0
        }
    },
    
    // DEX Protocol Information
    DEX_PROTOCOLS: {
        UNISWAP_V2: {
            name: 'Uniswap V2',
            version: '2',
            networks: ['ETHEREUM', 'POLYGON'],
            fee: 0.3 // 0.3%
        },
        UNISWAP_V3: {
            name: 'Uniswap V3',
            version: '3',
            networks: ['ETHEREUM', 'POLYGON', 'ARBITRUM', 'OPTIMISM'],
            fees: [0.01, 0.05, 0.3, 1.0] // Multiple fee tiers
        },
        PANCAKESWAP: {
            name: 'PancakeSwap',
            version: '2',
            networks: ['BSC'],
            fee: 0.25 // 0.25%
        },
        SUSHISWAP: {
            name: 'SushiSwap',
            version: '2',
            networks: ['ETHEREUM', 'POLYGON', 'ARBITRUM', 'AVALANCHE'],
            fee: 0.3 // 0.3%
        }
    },
    
    // Alert Types and Severities
    ALERTS: {
        TYPES: {
            NEW_TOKEN: 'new_token',
            ARBITRAGE: 'arbitrage',
            PRICE_ALERT: 'price_alert',
            SYSTEM: 'system',
            TRADE: 'trade',
            ERROR: 'error'
        },
        SEVERITIES: {
            INFO: {
                value: 'info',
                color: '#17a2b8',
                icon: 'bi-info-circle'
            },
            SUCCESS: {
                value: 'success',
                color: '#28a745',
                icon: 'bi-check-circle'
            },
            WARNING: {
                value: 'warning',
                color: '#ffc107',
                icon: 'bi-exclamation-triangle'
            },
            DANGER: {
                value: 'danger',
                color: '#dc3545',
                icon: 'bi-x-circle'
            }
        }
    },
    
    // Data Formatting
    FORMATTING: {
        CURRENCY: {
            USD: { symbol: '$', decimals: 2 },
            ETH: { symbol: 'Ξ', decimals: 4 },
            BTC: { symbol: '₿', decimals: 6 }
        },
        NUMBERS: {
            LARGE_NUMBER_THRESHOLD: 1000,
            PERCENTAGE_DECIMALS: 2,
            PRICE_DECIMALS: 6,
            VOLUME_DECIMALS: 2
        }
    },
    
    // Feature Flags
    FEATURES: {
        TOKEN_DISCOVERY: true,
        LIVE_TRADING: false,      // Phase 3B Week 5-6
        ARBITRAGE: false,         // Phase 3B Week 5-6
        AI_RISK: false,           // Phase 3B Week 7-8
        MOBILE_APP: false,        // Phase 3C
        ENTERPRISE: false,        // Phase 3C
        DARK_MODE: false,         // Future enhancement
        NOTIFICATIONS: true,
        WEBSOCKET: true,
        CACHING: true,
        ANALYTICS: false          // Phase 3B Week 7-8
    },
    
    // Storage Keys (for localStorage/sessionStorage)
    STORAGE_KEYS: {
        USER_PREFERENCES: 'dex_sniper_user_prefs',
        DASHBOARD_STATE: 'dex_sniper_dashboard_state',
        TOKEN_FILTERS: 'dex_sniper_token_filters',
        TRADING_SETTINGS: 'dex_sniper_trading_settings',
        THEME: 'dex_sniper_theme',
        NOTIFICATIONS_ENABLED: 'dex_sniper_notifications'
    },
    
    // Error Codes
    ERROR_CODES: {
        NETWORK_ERROR: 'NETWORK_ERROR',
        API_ERROR: 'API_ERROR',
        WEBSOCKET_ERROR: 'WEBSOCKET_ERROR',
        VALIDATION_ERROR: 'VALIDATION_ERROR',
        AUTHENTICATION_ERROR: 'AUTH_ERROR',
        RATE_LIMIT_ERROR: 'RATE_LIMIT_ERROR',
        UNKNOWN_ERROR: 'UNKNOWN_ERROR'
    },
    
    // HTTP Status Codes
    HTTP_STATUS: {
        OK: 200,
        CREATED: 201,
        NO_CONTENT: 204,
        BAD_REQUEST: 400,
        UNAUTHORIZED: 401,
        FORBIDDEN: 403,
        NOT_FOUND: 404,
        METHOD_NOT_ALLOWED: 405,
        CONFLICT: 409,
        TOO_MANY_REQUESTS: 429,
        INTERNAL_SERVER_ERROR: 500,
        BAD_GATEWAY: 502,
        SERVICE_UNAVAILABLE: 503,
        GATEWAY_TIMEOUT: 504
    },
    
    // Chart Configuration
    CHARTS: {
        DEFAULT_COLORS: [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
        ],
        GRID_COLOR: '#f0f0f0',
        TEXT_COLOR: '#666666',
        TOOLTIP_BACKGROUND: 'rgba(0, 0, 0, 0.8)',
        ANIMATION_DURATION: 1000
    },
    
    // Keyboard Shortcuts
    KEYBOARD_SHORTCUTS: {
        SEARCH: 'Ctrl+K',
        DASHBOARD: 'Ctrl+D',
        REFRESH: 'F5',
        HELP: 'F1',
        SETTINGS: 'Ctrl+,',
        ESCAPE: 'Escape'
    },
    
    // Performance Thresholds
    PERFORMANCE: {
        API_RESPONSE_WARNING: 1000, // 1 second
        API_RESPONSE_ERROR: 5000,   // 5 seconds
        WEBSOCKET_LATENCY_WARNING: 500, // 500ms
        WEBSOCKET_LATENCY_ERROR: 2000,  // 2 seconds
        MEMORY_USAGE_WARNING: 100,      // 100MB
        CACHE_SIZE_LIMIT: 50            // 50 items
    },
    
    // Validation Rules
    VALIDATION: {
        TOKEN_ADDRESS_REGEX: /^0x[a-fA-F0-9]{40}$/,
        EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        PASSWORD_MIN_LENGTH: 8,
        USERNAME_MIN_LENGTH: 3,
        USERNAME_MAX_LENGTH: 20,
        MIN_AMOUNT: 0.000001,
        MAX_AMOUNT: 1000000
    }
};

// Utility functions for constants
window.APP_CONSTANTS.UTILS = {
    /**
     * Get network by chain ID
     */
    getNetworkByChainId(chainId) {
        return Object.values(window.APP_CONSTANTS.NETWORKS)
            .find(network => network.chainId === chainId);
    },
    
    /**
     * Get risk level by score
     */
    getRiskLevel(score) {
        if (score <= window.APP_CONSTANTS.RISK_LEVELS.LOW.threshold) {
            return window.APP_CONSTANTS.RISK_LEVELS.LOW;
        } else if (score <= window.APP_CONSTANTS.RISK_LEVELS.MEDIUM.threshold) {
            return window.APP_CONSTANTS.RISK_LEVELS.MEDIUM;
        } else {
            return window.APP_CONSTANTS.RISK_LEVELS.HIGH;
        }
    },
    
    /**
     * Check if feature is enabled
     */
    isFeatureEnabled(featureName) {
        return window.APP_CONSTANTS.FEATURES[featureName] === true;
    },
    
    /**
     * Get formatted network list
     */
    getNetworkList() {
        return Object.entries(window.APP_CONSTANTS.NETWORKS)
            .map(([key, network]) => ({
                key,
                ...network
            }));
    },
    
    /**
     * Get supported DEX protocols for network
     */
    getDexProtocols(networkKey) {
        return Object.values(window.APP_CONSTANTS.DEX_PROTOCOLS)
            .filter(protocol => protocol.networks.includes(networkKey));
    }
};

// Freeze constants to prevent modification
Object.freeze(window.APP_CONSTANTS.NETWORKS);
Object.freeze(window.APP_CONSTANTS.RISK_LEVELS);
Object.freeze(window.APP_CONSTANTS.DEX_PROTOCOLS);
Object.freeze(window.APP_CONSTANTS.ALERTS);
Object.freeze(window.APP_CONSTANTS.FEATURES);
Object.freeze(window.APP_CONSTANTS);

console.log('📋 Application constants loaded:', window.APP_CONSTANTS.APP_NAME, window.APP_CONSTANTS.VERSION);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.APP_CONSTANTS;
}