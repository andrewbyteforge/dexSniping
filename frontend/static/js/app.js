/**
 * Main Application Controller
 * File: frontend/static/js/app.js
 * 
 * Central application controller for DEX Sniper Pro dashboard.
 * Manages routing, component initialization, and global state.
 */

class DexSniperApp {
    constructor() {
        this.config = window.DEX_SNIPER_CONFIG || {};
        this.isInitialized = false;
        this.currentSection = 'dashboard';
        this.components = {};
        
        // Performance monitoring
        this.performanceMonitor = window.PERFORMANCE_MONITOR || {};
        
        // Application state
        this.state = {
            isConnected: false,
            lastUpdate: null,
            userData: null,
            notifications: [],
            errors: []
        };
        
        // Event emitter for component communication
        this.events = new EventTarget();
        
        console.log('🚀 DexSniperApp initialized');
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('🔄 Starting DEX Sniper Pro initialization...');
            
            // Check if already initialized
            if (this.isInitialized) {
                console.warn('⚠️ Application already initialized');
                return;
            }
            
            // Initialize core systems
            await this.initializeCore();
            
            // Initialize components
            await this.initializeComponents();
            
            // Setup navigation
            this.setupNavigation();
            
            // Setup sidebar
            this.setupSidebar();
            
            // Initialize API client
            await this.initializeApiClient();
            
            // Initialize WebSocket
            await this.initializeWebSocket();
            
            // Load initial data
            await this.loadInitialData();
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
            // Setup error handling
            this.setupErrorHandling();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('✅ DEX Sniper Pro initialization complete');
            
            // Emit initialization complete event
            this.events.dispatchEvent(new CustomEvent('app:initialized'));
            
        } catch (error) {
            console.error('❌ DEX Sniper Pro initialization failed:', error);
            this.handleInitializationError(error);
            throw error;
        }
    }

    /**
     * Initialize core application systems
     */
    async initializeCore() {
        console.log('🔧 Initializing core systems...');
        
        // Validate configuration
        if (!this.config.API_BASE_URL) {
            throw new Error('API_BASE_URL not configured');
        }
        
        // Initialize utilities
        if (typeof Formatters !== 'undefined') {
            this.formatters = new Formatters();
        }
        
        if (typeof Validators !== 'undefined') {
            this.validators = new Validators();
        }
        
        console.log('✅ Core systems initialized');
    }

    /**
     * Initialize application components
     */
    async initializeComponents() {
        console.log('🔧 Initializing components...');
        
        try {
            // Initialize Dashboard Controller
            if (typeof DashboardController !== 'undefined') {
                this.components.dashboard = new DashboardController(this);
                await this.components.dashboard.init();
            }
            
            // Initialize Token Discovery Controller
            if (typeof TokenDiscoveryController !== 'undefined') {
                this.components.tokenDiscovery = new TokenDiscoveryController(this);
                await this.components.tokenDiscovery.init();
            }
            
            // Initialize Trading Controller (Phase 3B)
            if (typeof TradingController !== 'undefined' && this.config.FEATURES.LIVE_TRADING) {
                this.components.trading = new TradingController(this);
                await this.components.trading.init();
            }
            
            // Initialize Chart Controller
            if (typeof ChartController !== 'undefined') {
                this.components.charts = new ChartController(this);
                await this.components.charts.init();
            }
            
            console.log('✅ Components initialized:', Object.keys(this.components));
            
        } catch (error) {
            console.error('❌ Component initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup navigation system
     */
    setupNavigation() {
        console.log('🔧 Setting up navigation...');
        
        // Setup navigation links
        document.querySelectorAll('.nav-link[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const sectionId = e.target.closest('[data-section]').getAttribute('data-section');
                this.showSection(sectionId);
            });
        });
        
        // Setup browser history
        window.addEventListener('popstate', (e) => {
            const section = e.state?.section || this.getSectionFromHash();
            this.showSection(section, false);
        });
        
        // Load initial section
        const initialSection = this.getSectionFromHash() || 'dashboard';
        this.showSection(initialSection, false);
        
        console.log('✅ Navigation setup complete');
    }

    /**
     * Setup sidebar functionality
     */
    setupSidebar() {
        console.log('🔧 Setting up sidebar...');
        
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('show');
                overlay?.classList.toggle('show');
            });
        }
        
        // Close sidebar when clicking overlay
        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar?.classList.remove('show');
                overlay.classList.remove('show');
            });
        }
        
        // Auto-hide sidebar on small screens when navigating
        if (window.innerWidth < 768) {
            this.events.addEventListener('section:changed', () => {
                sidebar?.classList.remove('show');
                overlay?.classList.remove('show');
            });
        }
        
        console.log('✅ Sidebar setup complete');
    }

    /**
     * Initialize API client
     */
    async initializeApiClient() {
        console.log('🔧 Initializing API client...');
        
        if (typeof ApiClient !== 'undefined') {
            this.api = new ApiClient(this.config.API_BASE_URL);
            
            // Test API connection
            try {
                const healthCheck = await this.api.get('/health');
                console.log('✅ API connection established:', healthCheck.status);
                this.updateConnectionStatus(true);
            } catch (error) {
                console.warn('⚠️ API connection failed:', error);
                this.updateConnectionStatus(false);
            }
        } else {
            console.warn('⚠️ ApiClient not available');
        }
    }

    /**
     * Initialize WebSocket connection
     */
    async initializeWebSocket() {
        console.log('🔧 Initializing WebSocket...');
        
        if (typeof WebSocketManager !== 'undefined') {
            this.websocket = new WebSocketManager(this.config.WEBSOCKET_URL);
            
            // Setup WebSocket event handlers
            this.websocket.on('connect', () => {
                console.log('✅ WebSocket connected');
                this.updateConnectionStatus(true);
            });
            
            this.websocket.on('disconnect', () => {
                console.log('🔌 WebSocket disconnected');
                this.updateConnectionStatus(false);
            });
            
            this.websocket.on('stats_update', (data) => {
                this.handleStatsUpdate(data);
            });
            
            this.websocket.on('token_discovery', (data) => {
                this.handleTokenDiscovery(data);
            });
            
            this.websocket.on('live_alert', (data) => {
                this.handleLiveAlert(data);
            });
            
            // Connect
            await this.websocket.connect();
        } else {
            console.warn('⚠️ WebSocketManager not available');
        }
    }

    /**
     * Load initial application data
     */
    async loadInitialData() {
        console.log('🔧 Loading initial data...');
        
        try {
            // Load dashboard stats
            if (this.components.dashboard) {
                await this.components.dashboard.loadStats();
            }
            
            // Load token discovery data
            if (this.components.tokenDiscovery) {
                await this.components.tokenDiscovery.loadTokens();
            }
            
            console.log('✅ Initial data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
            this.showError('Failed to load initial data. Some features may not work correctly.');
        }
    }

    /**
     * Start real-time updates
     */
    startRealTimeUpdates() {
        console.log('🔧 Starting real-time updates...');
        
        // Dashboard stats update
        setInterval(() => {
            if (this.components.dashboard && this.currentSection === 'dashboard') {
                this.components.dashboard.updateStats();
            }
        }, this.config.REFRESH_INTERVALS.STATS);
        
        // Token discovery update
        setInterval(() => {
            if (this.components.tokenDiscovery && 
                (this.currentSection === 'dashboard' || this.currentSection === 'token-discovery')) {
                this.components.tokenDiscovery.refreshTokens();
            }
        }, this.config.REFRESH_INTERVALS.TOKENS);
        
        console.log('✅ Real-time updates started');
    }

    /**
     * Setup global error handling
     */
    setupErrorHandling() {
        // API error handling
        if (this.api) {
            this.api.on('error', (error) => {
                this.handleApiError(error);
            });
        }
        
        // WebSocket error handling
        if (this.websocket) {
            this.websocket.on('error', (error) => {
                this.handleWebSocketError(error);
            });
        }
    }

    /**
     * Show specific section
     */
    showSection(sectionId, updateHistory = true) {
        console.log(`🔄 Switching to section: ${sectionId}`);
        
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show target section
        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.classList.add('fade-in');
        }
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-section="${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // Update browser history
        if (updateHistory) {
            const url = new URL(window.location);
            url.hash = sectionId;
            window.history.pushState({ section: sectionId }, '', url);
        }
        
        // Update current section
        this.currentSection = sectionId;
        
        // Emit section change event
        this.events.dispatchEvent(new CustomEvent('section:changed', {
            detail: { section: sectionId }
        }));
        
        // Initialize section-specific components
        this.initializeSectionComponents(sectionId);
    }

    /**
     * Initialize components for specific section
     */
    initializeSectionComponents(sectionId) {
        switch (sectionId) {
            case 'dashboard':
                if (this.components.dashboard) {
                    this.components.dashboard.onSectionShow();
                }
                break;
            case 'token-discovery':
                if (this.components.tokenDiscovery) {
                    this.components.tokenDiscovery.onSectionShow();
                }
                break;
            case 'live-trading':
                if (this.components.trading) {
                    this.components.trading.onSectionShow();
                }
                break;
        }
    }

    /**
     * Get section from URL hash
     */
    getSectionFromHash() {
        const hash = window.location.hash.replace('#', '');
        return hash || 'dashboard';
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(isConnected) {
        this.state.isConnected = isConnected;
        
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = isConnected ? 'Live' : 'Disconnected';
            statusElement.className = isConnected ? 'text-success' : 'text-danger';
        }
        
        // Update sidebar status
        const sidebarStatus = document.querySelector('.system-status');
        if (sidebarStatus) {
            const apiStatus = sidebarStatus.querySelector('.status-item:nth-child(2) .status-dot');
            const wsStatus = sidebarStatus.querySelector('.status-item:nth-child(3) .status-dot');
            
            if (apiStatus) {
                apiStatus.className = `status-dot ${isConnected ? 'status-success' : 'status-danger'}`;
            }
            
            if (wsStatus) {
                wsStatus.className = `status-dot ${isConnected ? 'status-success' : 'status-warning'}`;
            }
        }
    }

    /**
     * Handle stats update from WebSocket
     */
    handleStatsUpdate(data) {
        if (this.components.dashboard) {
            this.components.dashboard.updateStatsDisplay(data);
        }
        
        // Update sidebar quick stats
        this.updateSidebarStats(data);
    }

    /**
     * Handle token discovery update from WebSocket
     */
    handleTokenDiscovery(data) {
        if (this.components.tokenDiscovery) {
            this.components.tokenDiscovery.updateTokens(data);
        }
    }

    /**
     * Handle live alert from WebSocket
     */
    handleLiveAlert(alert) {
        this.showNotification(alert.title, alert.message, alert.severity);
    }

    /**
     * Update sidebar quick stats
     */
    updateSidebarStats(stats) {
        const elements = {
            'sidebar-tokens': stats.tokens_discovered || 0,
            'sidebar-trades': stats.active_trades || 0,
            'sidebar-arb': stats.arbitrage_opportunities || 0
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    /**
     * Show notification to user
     */
    showNotification(title, message, type = 'info') {
        const notification = {
            id: Date.now(),
            title,
            message,
            type,
            timestamp: new Date()
        };
        
        this.state.notifications.push(notification);
        
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Show error message
     */
    showError(message, details = null) {
        console.error('Application Error:', message, details);
        
        this.state.errors.push({
            message,
            details,
            timestamp: new Date()
        });
        
        this.showNotification('Error', message, 'danger');
    }

    /**
     * Handle initialization error
     */
    handleInitializationError(error) {
        console.error('❌ Initialization Error:', error);
        
        // Show user-friendly error message
        const errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger m-3';
        errorContainer.innerHTML = `
            <h4 class="alert-heading">
                <i class="bi bi-exclamation-triangle"></i>
                Application Error
            </h4>
            <p>The DEX Sniper Pro dashboard failed to initialize properly.</p>
            <hr>
            <p class="mb-0">
                <button class="btn btn-outline-danger" onclick="window.location.reload()">
                    <i class="bi bi-arrow-clockwise"></i>
                    Reload Application
                </button>
            </p>
        `;
        
        document.body.prepend(errorContainer);
    }

    /**
     * Handle API errors
     */
    handleApiError(error) {
        console.error('API Error:', error);
        
        if (error.status === 429) {
            this.showError('Rate limit exceeded. Please slow down your requests.');
        } else if (error.status >= 500) {
            this.showError('Server error. Please try again later.');
        } else if (error.status === 401) {
            this.showError('Authentication required. Please log in.');
        } else {
            this.showError('An API error occurred. Please check your connection.');
        }
    }

    /**
     * Handle WebSocket errors
     */
    handleWebSocketError(error) {
        console.error('WebSocket Error:', error);
        this.showError('Real-time connection lost. Attempting to reconnect...');
    }

    /**
     * Get application state for debugging
     */
    getState() {
        return {
            ...this.state,
            currentSection: this.currentSection,
            isInitialized: this.isInitialized,
            components: Object.keys(this.components),
            performance: this.performanceMonitor
        };
    }
}

// Create global instance
window.DexSniperApp = new DexSniperApp();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DexSniperApp;
}