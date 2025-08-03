/**
 * Token Discovery Controller Module
 * File: frontend/static/js/components/token-discovery-controller.js
 * 
 * Advanced token discovery coordination for DEX Sniper Pro.
 * Manages token scanning, filtering, watchlists, and real-time updates.
 */

class TokenDiscoveryController {
    constructor(app) {
        this.app = app;
        this.isInitialized = false;
        this.isDiscovering = false;
        this.discoveryInterval = null;
        
        // Component references
        this.components = {
            table: null,
            filters: null,
            search: null
        };
        
        // Discovery state
        this.state = {
            tokens: [],
            filteredTokens: [],
            watchlist: new Set(),
            filters: {
                riskLevel: 'all',
                minLiquidity: 0,
                maxAge: 24,
                networks: [],
                searchQuery: ''
            },
            pagination: {
                currentPage: 1,
                itemsPerPage: 20,
                totalItems: 0,
                totalPages: 0
            },
            sorting: {
                field: 'discovered_at',
                direction: 'desc'
            }
        };
        
        // Configuration
        this.config = {
            discoveryInterval: window.APP_CONSTANTS?.REFRESH_INTERVALS?.TOKENS || 30000,
            maxTokens: 1000,
            riskThresholds: {
                low: 30,
                medium: 70,
                high: 100
            },
            networks: window.APP_CONSTANTS?.NETWORKS || {},
            apiEndpoints: {
                discover: '/tokens/discover',
                details: '/tokens/{address}',
                watchlist: '/tokens/watchlist'
            }
        };
        
        console.log('🔍 Token Discovery Controller created');
    }

    /**
     * Initialize the token discovery controller
     */
    async init() {
        try {
            console.log('🔧 Initializing Token Discovery Controller...');
            
            // Connect to existing components
            this.connectComponents();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            // Setup discovery automation
            this.setupDiscoveryAutomation();
            
            this.isInitialized = true;
            console.log('✅ Token Discovery Controller initialized');
            
            // Emit initialization event
            this.app.events.dispatchEvent(new CustomEvent('tokenDiscovery:initialized'));
            
        } catch (error) {
            console.error('❌ Token Discovery Controller initialization failed:', error);
            this.handleError('Initialization failed', error);
            throw error;
        }
    }

    /**
     * Connect to existing token discovery components
     */
    connectComponents() {
        try {
            // Connect to Token Discovery Table component
            if (typeof window.TokenDiscoveryTable !== 'undefined') {
                this.components.table = window.TokenDiscoveryTable;
                console.log('✅ Token Discovery Table connected');
            } else {
                console.warn('⚠️ Token Discovery Table component not found');
            }
            
            // Cache DOM elements for filters and controls
            this.cacheFilterElements();
            
        } catch (error) {
            console.error('❌ Failed to connect components:', error);
        }
    }

    /**
     * Cache filter DOM elements
     */
    cacheFilterElements() {
        this.elements = {
            // Search elements
            searchInput: document.getElementById('token-search'),
            clearSearch: document.getElementById('clear-search'),
            
            // Filter elements
            riskFilter: document.getElementById('risk-filter'),
            liquidityFilter: document.getElementById('liquidity-filter'),
            ageFilter: document.getElementById('age-filter'),
            networkFilter: document.getElementById('network-filter'),
            
            // Control elements
            startButton: document.getElementById('start-discovery'),
            pauseButton: document.getElementById('pause-discovery'),
            refreshButton: document.getElementById('refresh-tokens'),
            
            // Status elements
            discoveryStatus: document.getElementById('discovery-status'),
            tokenCount: document.getElementById('token-count'),
            lastUpdate: document.getElementById('last-token-update'),
            
            // Pagination elements
            pagination: document.getElementById('token-pagination'),
            itemsPerPageSelect: document.getElementById('items-per-page'),
            
            // Sorting elements
            sortField: document.getElementById('sort-field'),
            sortDirection: document.getElementById('sort-direction')
        };
        
        console.log('✅ Filter elements cached');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        try {
            console.log('🔧 Setting up token discovery event listeners...');
            
            // Search functionality
            if (this.elements.searchInput) {
                this.elements.searchInput.addEventListener('input', 
                    this.debounce((e) => this.handleSearchInput(e.target.value), 500)
                );
            }
            
            if (this.elements.clearSearch) {
                this.elements.clearSearch.addEventListener('click', () => this.clearSearch());
            }
            
            // Filter controls
            if (this.elements.riskFilter) {
                this.elements.riskFilter.addEventListener('change', (e) => 
                    this.updateFilter('riskLevel', e.target.value)
                );
            }
            
            if (this.elements.liquidityFilter) {
                this.elements.liquidityFilter.addEventListener('input', (e) => 
                    this.updateFilter('minLiquidity', parseFloat(e.target.value) || 0)
                );
            }
            
            if (this.elements.ageFilter) {
                this.elements.ageFilter.addEventListener('change', (e) => 
                    this.updateFilter('maxAge', parseInt(e.target.value) || 24)
                );
            }
            
            if (this.elements.networkFilter) {
                this.elements.networkFilter.addEventListener('change', (e) => 
                    this.updateNetworkFilter(e.target.value)
                );
            }
            
            // Discovery controls
            if (this.elements.startButton) {
                this.elements.startButton.addEventListener('click', () => this.startDiscovery());
            }
            
            if (this.elements.pauseButton) {
                this.elements.pauseButton.addEventListener('click', () => this.stopDiscovery());
            }
            
            if (this.elements.refreshButton) {
                this.elements.refreshButton.addEventListener('click', () => this.refreshTokens());
            }
            
            // Pagination controls
            if (this.elements.itemsPerPageSelect) {
                this.elements.itemsPerPageSelect.addEventListener('change', (e) => 
                    this.updateItemsPerPage(parseInt(e.target.value))
                );
            }
            
            // Sorting controls
            if (this.elements.sortField) {
                this.elements.sortField.addEventListener('change', (e) => 
                    this.updateSorting(e.target.value, this.state.sorting.direction)
                );
            }
            
            if (this.elements.sortDirection) {
                this.elements.sortDirection.addEventListener('change', (e) => 
                    this.updateSorting(this.state.sorting.field, e.target.value)
                );
            }
            
            // WebSocket events
            if (this.app.websocket) {
                this.app.websocket.on('token_discovery', (data) => {
                    this.handleTokenUpdate(data);
                });
                
                this.app.websocket.on('token_price_update', (data) => {
                    this.handlePriceUpdate(data);
                });
            }
            
            // App events
            this.app.events.addEventListener('app:online', () => {
                this.handleConnectionChange(true);
            });
            
            this.app.events.addEventListener('app:offline', () => {
                this.handleConnectionChange(false);
            });
            
            // Table events
            document.addEventListener('token:watchlist:add', (event) => {
                this.addToWatchlist(event.detail.address);
            });
            
            document.addEventListener('token:watchlist:remove', (event) => {
                this.removeFromWatchlist(event.detail.address);
            });
            
            document.addEventListener('token:details:view', (event) => {
                this.viewTokenDetails(event.detail.address);
            });
            
            console.log('✅ Token discovery event listeners setup');
            
        } catch (error) {
            console.error('❌ Failed to setup event listeners:', error);
        }
    }

    /**
     * Load initial token discovery data
     */
    async loadInitialData() {
        try {
            console.log('🔧 Loading initial token data...');
            
            // Load saved watchlist
            this.loadWatchlist();
            
            // Load initial tokens
            await this.loadTokens();
            
            // Apply initial filters
            this.applyFilters();
            
            console.log('✅ Initial token data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
            this.handleError('Failed to load token data', error);
        }
    }

    /**
     * Load tokens from API
     */
    async loadTokens(append = false) {
        try {
            if (!this.app.apiClient) {
                throw new Error('API Client not available');
            }
            
            const params = {
                limit: this.state.pagination.itemsPerPage,
                offset: append ? this.state.tokens.length : 0,
                sort_field: this.state.sorting.field,
                sort_direction: this.state.sorting.direction
            };
            
            // Add filters to params
            if (this.state.filters.riskLevel !== 'all') {
                const riskRange = this.getRiskRange(this.state.filters.riskLevel);
                params.min_risk = riskRange.min;
                params.max_risk = riskRange.max;
            }
            
            if (this.state.filters.minLiquidity > 0) {
                params.min_liquidity = this.state.filters.minLiquidity;
            }
            
            if (this.state.filters.maxAge < 24) {
                params.max_age_hours = this.state.filters.maxAge;
            }
            
            if (this.state.filters.networks.length > 0) {
                params.networks = this.state.filters.networks.join(',');
            }
            
            const response = await this.app.apiClient.get(
                this.config.apiEndpoints.discover, 
                params
            );
            
            if (response && response.data) {
                const newTokens = response.data.tokens || [];
                
                if (append) {
                    this.state.tokens = [...this.state.tokens, ...newTokens];
                } else {
                    this.state.tokens = newTokens;
                }
                
                // Update pagination info
                this.state.pagination.totalItems = response.data.total || newTokens.length;
                this.state.pagination.totalPages = Math.ceil(
                    this.state.pagination.totalItems / this.state.pagination.itemsPerPage
                );
                
                // Apply filters and update display
                this.applyFilters();
                this.updateDisplay();
                
                console.log(`✅ Loaded ${newTokens.length} tokens`);
            }
            
        } catch (error) {
            console.error('❌ Failed to load tokens:', error);
            this.handleError('Failed to load tokens', error);
        }
    }

    /**
     * Setup discovery automation
     */
    setupDiscoveryAutomation() {
        try {
            // Auto-discovery based on configuration
            const autoStart = window.APP_CONSTANTS?.FEATURES?.AUTO_DISCOVERY || false;
            
            if (autoStart) {
                this.startDiscovery();
            }
            
        } catch (error) {
            console.error('❌ Failed to setup discovery automation:', error);
        }
    }

    // Discovery Control Methods

    /**
     * Start token discovery
     */
    startDiscovery() {
        try {
            if (this.isDiscovering) {
                console.warn('⚠️ Discovery already running');
                return;
            }
            
            console.log('🔍 Starting token discovery...');
            
            this.isDiscovering = true;
            this.updateDiscoveryStatus('running');
            
            // Start discovery interval
            this.discoveryInterval = setInterval(() => {
                this.performDiscoveryScans();
            }, this.config.discoveryInterval);
            
            // Immediate scan
            this.performDiscoveryScans();
            
            // Update UI
            this.updateDiscoveryControls();
            
            // Emit event
            this.app.events.dispatchEvent(new CustomEvent('tokenDiscovery:started'));
            
        } catch (error) {
            console.error('❌ Failed to start discovery:', error);
            this.handleError('Failed to start discovery', error);
        }
    }

    /**
     * Stop token discovery
     */
    stopDiscovery() {
        try {
            if (!this.isDiscovering) {
                console.warn('⚠️ Discovery not running');
                return;
            }
            
            console.log('⏹️ Stopping token discovery...');
            
            this.isDiscovering = false;
            this.updateDiscoveryStatus('stopped');
            
            // Clear discovery interval
            if (this.discoveryInterval) {
                clearInterval(this.discoveryInterval);
                this.discoveryInterval = null;
            }
            
            // Update UI
            this.updateDiscoveryControls();
            
            // Emit event
            this.app.events.dispatchEvent(new CustomEvent('tokenDiscovery:stopped'));
            
        } catch (error) {
            console.error('❌ Failed to stop discovery:', error);
        }
    }

    /**
     * Perform discovery scans
     */
    async performDiscoveryScans() {
        try {
            console.log('🔍 Performing discovery scan...');
            
            // Load new tokens (append to existing)
            await this.loadTokens(false);
            
            // Update last scan time
            this.updateLastScanTime();
            
        } catch (error) {
            console.error('❌ Discovery scan failed:', error);
            this.handleError('Discovery scan failed', error);
        }
    }

    /**
     * Refresh tokens manually
     */
    async refreshTokens() {
        try {
            console.log('🔄 Refreshing tokens...');
            
            // Clear existing tokens and reload
            this.state.tokens = [];
            await this.loadTokens(false);
            
            console.log('✅ Tokens refreshed');
            
        } catch (error) {
            console.error('❌ Failed to refresh tokens:', error);
            this.handleError('Failed to refresh tokens', error);
        }
    }

    // Filter and Search Methods

    /**
     * Handle search input
     */
    handleSearchInput(query) {
        try {
            this.state.filters.searchQuery = query.trim().toLowerCase();
            this.applyFilters();
            this.updateDisplay();
            
            console.log(`🔍 Search query updated: "${query}"`);
            
        } catch (error) {
            console.error('❌ Search failed:', error);
        }
    }

    /**
     * Clear search
     */
    clearSearch() {
        try {
            this.state.filters.searchQuery = '';
            
            if (this.elements.searchInput) {
                this.elements.searchInput.value = '';
            }
            
            this.applyFilters();
            this.updateDisplay();
            
            console.log('🔍 Search cleared');
            
        } catch (error) {
            console.error('❌ Failed to clear search:', error);
        }
    }

    /**
     * Update filter
     */
    updateFilter(filterName, value) {
        try {
            this.state.filters[filterName] = value;
            this.applyFilters();
            this.updateDisplay();
            
            console.log(`🔧 Filter updated: ${filterName} = ${value}`);
            
        } catch (error) {
            console.error('❌ Failed to update filter:', error);
        }
    }

    /**
     * Update network filter
     */
    updateNetworkFilter(networkValue) {
        try {
            if (networkValue === 'all') {
                this.state.filters.networks = [];
            } else {
                const networks = networkValue.split(',').filter(n => n.trim());
                this.state.filters.networks = networks;
            }
            
            this.applyFilters();
            this.updateDisplay();
            
            console.log(`🌐 Network filter updated: ${this.state.filters.networks.join(', ')}`);
            
        } catch (error) {
            console.error('❌ Failed to update network filter:', error);
        }
    }

    /**
     * Apply all filters to tokens
     */
    applyFilters() {
        try {
            let filtered = [...this.state.tokens];
            
            // Search filter
            if (this.state.filters.searchQuery) {
                const query = this.state.filters.searchQuery;
                filtered = filtered.filter(token => 
                    token.name?.toLowerCase().includes(query) ||
                    token.symbol?.toLowerCase().includes(query) ||
                    token.address?.toLowerCase().includes(query)
                );
            }
            
            // Risk level filter
            if (this.state.filters.riskLevel !== 'all') {
                const riskRange = this.getRiskRange(this.state.filters.riskLevel);
                filtered = filtered.filter(token => 
                    token.risk_score >= riskRange.min && 
                    token.risk_score <= riskRange.max
                );
            }
            
            // Liquidity filter
            if (this.state.filters.minLiquidity > 0) {
                filtered = filtered.filter(token => 
                    (token.liquidity || 0) >= this.state.filters.minLiquidity
                );
            }
            
            // Age filter
            if (this.state.filters.maxAge < 24) {
                const maxAgeMs = this.state.filters.maxAge * 60 * 60 * 1000;
                const now = Date.now();
                
                filtered = filtered.filter(token => {
                    const tokenAge = now - new Date(token.discovered_at).getTime();
                    return tokenAge <= maxAgeMs;
                });
            }
            
            // Network filter
            if (this.state.filters.networks.length > 0) {
                filtered = filtered.filter(token => 
                    this.state.filters.networks.includes(token.network)
                );
            }
            
            this.state.filteredTokens = filtered;
            
            // Update pagination
            this.state.pagination.totalItems = filtered.length;
            this.state.pagination.totalPages = Math.ceil(
                filtered.length / this.state.pagination.itemsPerPage
            );
            
            // Reset to first page if current page is invalid
            if (this.state.pagination.currentPage > this.state.pagination.totalPages) {
                this.state.pagination.currentPage = 1;
            }
            
        } catch (error) {
            console.error('❌ Failed to apply filters:', error);
        }
    }

    /**
     * Get risk range for filter level
     */
    getRiskRange(level) {
        switch (level) {
            case 'low':
                return { min: 0, max: this.config.riskThresholds.low };
            case 'medium':
                return { min: this.config.riskThresholds.low, max: this.config.riskThresholds.medium };
            case 'high':
                return { min: this.config.riskThresholds.medium, max: this.config.riskThresholds.high };
            default:
                return { min: 0, max: 100 };
        }
    }

    // Sorting and Pagination Methods

    /**
     * Update sorting
     */
    updateSorting(field, direction) {
        try {
            this.state.sorting.field = field;
            this.state.sorting.direction = direction;
            
            // Sort filtered tokens
            this.sortTokens();
            this.updateDisplay();
            
            console.log(`📊 Sorting updated: ${field} ${direction}`);
            
        } catch (error) {
            console.error('❌ Failed to update sorting:', error);
        }
    }

    /**
     * Sort tokens by current criteria
     */
    sortTokens() {
        try {
            const { field, direction } = this.state.sorting;
            const multiplier = direction === 'asc' ? 1 : -1;
            
            this.state.filteredTokens.sort((a, b) => {
                let valueA = a[field];
                let valueB = b[field];
                
                // Handle different data types
                if (typeof valueA === 'string') {
                    valueA = valueA.toLowerCase();
                    valueB = valueB.toLowerCase();
                } else if (valueA instanceof Date) {
                    valueA = valueA.getTime();
                    valueB = valueB.getTime();
                } else if (typeof valueA === 'number') {
                    valueA = valueA || 0;
                    valueB = valueB || 0;
                }
                
                if (valueA < valueB) return -1 * multiplier;
                if (valueA > valueB) return 1 * multiplier;
                return 0;
            });
            
        } catch (error) {
            console.error('❌ Failed to sort tokens:', error);
        }
    }

    /**
     * Update items per page
     */
    updateItemsPerPage(itemsPerPage) {
        try {
            this.state.pagination.itemsPerPage = itemsPerPage;
            this.state.pagination.currentPage = 1;
            
            // Recalculate total pages
            this.state.pagination.totalPages = Math.ceil(
                this.state.filteredTokens.length / itemsPerPage
            );
            
            this.updateDisplay();
            
            console.log(`📄 Items per page updated: ${itemsPerPage}`);
            
        } catch (error) {
            console.error('❌ Failed to update items per page:', error);
        }
    }

    /**
     * Go to page
     */
    goToPage(page) {
        try {
            if (page < 1 || page > this.state.pagination.totalPages) {
                return;
            }
            
            this.state.pagination.currentPage = page;
            this.updateDisplay();
            
            console.log(`📄 Page changed: ${page}`);
            
        } catch (error) {
            console.error('❌ Failed to change page:', error);
        }
    }

    // Watchlist Methods

    /**
     * Load watchlist from storage
     */
    loadWatchlist() {
        try {
            const saved = localStorage.getItem('tokenDiscoveryWatchlist');
            if (saved) {
                const addresses = JSON.parse(saved);
                this.state.watchlist = new Set(addresses);
                console.log(`✅ Loaded ${addresses.length} watchlist items`);
            }
        } catch (error) {
            console.error('❌ Failed to load watchlist:', error);
        }
    }

    /**
     * Save watchlist to storage
     */
    saveWatchlist() {
        try {
            const addresses = Array.from(this.state.watchlist);
            localStorage.setItem('tokenDiscoveryWatchlist', JSON.stringify(addresses));
        } catch (error) {
            console.error('❌ Failed to save watchlist:', error);
        }
    }

    /**
     * Add token to watchlist
     */
    addToWatchlist(address) {
        try {
            this.state.watchlist.add(address);
            this.saveWatchlist();
            
            console.log(`⭐ Added to watchlist: ${address}`);
            
            // Emit event
            this.app.events.dispatchEvent(new CustomEvent('watchlist:added', {
                detail: { address }
            }));
            
        } catch (error) {
            console.error('❌ Failed to add to watchlist:', error);
        }
    }

    /**
     * Remove token from watchlist
     */
    removeFromWatchlist(address) {
        try {
            this.state.watchlist.delete(address);
            this.saveWatchlist();
            
            console.log(`❌ Removed from watchlist: ${address}`);
            
            // Emit event
            this.app.events.dispatchEvent(new CustomEvent('watchlist:removed', {
                detail: { address }
            }));
            
        } catch (error) {
            console.error('❌ Failed to remove from watchlist:', error);
        }
    }

    // Event Handlers

    /**
     * Handle WebSocket token update
     */
    handleTokenUpdate(data) {
        try {
            if (data.token) {
                const token = data.token;
                
                // Find existing token or add new one
                const existingIndex = this.state.tokens.findIndex(
                    t => t.address === token.address
                );
                
                if (existingIndex >= 0) {
                    this.state.tokens[existingIndex] = token;
                } else {
                    this.state.tokens.unshift(token);
                    
                    // Limit total tokens
                    if (this.state.tokens.length > this.config.maxTokens) {
                        this.state.tokens = this.state.tokens.slice(0, this.config.maxTokens);
                    }
                }
                
                // Reapply filters and update display
                this.applyFilters();
                this.updateDisplay();
                
                console.log(`🪙 Token updated: ${token.symbol}`);
            }
            
        } catch (error) {
            console.error('❌ Failed to handle token update:', error);
        }
    }

    /**
     * Handle price update
     */
    handlePriceUpdate(data) {
        try {
            if (data.address && data.price) {
                const token = this.state.tokens.find(t => t.address === data.address);
                if (token) {
                    token.price = data.price;
                    token.price_change_24h = data.price_change_24h;
                    
                    // Update display if token is currently visible
                    this.updateDisplay();
                }
            }
            
        } catch (error) {
            console.error('❌ Failed to handle price update:', error);
        }
    }

    /**
     * Handle connection change
     */
    handleConnectionChange(isOnline) {
        if (isOnline) {
            // Resume discovery if it was active
            if (this.isDiscovering && !this.discoveryInterval) {
                this.startDiscovery();
            }
        } else {
            // Pause discovery when offline
            if (this.discoveryInterval) {
                clearInterval(this.discoveryInterval);
                this.discoveryInterval = null;
            }
        }
        
        this.updateDiscoveryStatus(isOnline ? 'running' : 'offline');
    }

    /**
     * View token details
     */
    async viewTokenDetails(address) {
        try {
            console.log(`🔍 Viewing details for token: ${address}`);
            
            // This would typically open a modal or navigate to a details page
            // For now, just emit an event
            this.app.events.dispatchEvent(new CustomEvent('token:details:open', {
                detail: { address }
            }));
            
        } catch (error) {
            console.error('❌ Failed to view token details:', error);
        }
    }

    // UI Update Methods

    /**
     * Update display with current filtered tokens
     */
    updateDisplay() {
        try {
            // Get paginated tokens
            const startIndex = (this.state.pagination.currentPage - 1) * this.state.pagination.itemsPerPage;
            const endIndex = startIndex + this.state.pagination.itemsPerPage;
            const paginatedTokens = this.state.filteredTokens.slice(startIndex, endIndex);
            
            // Update table component
            if (this.components.table && typeof this.components.table.updateTokens === 'function') {
                this.components.table.updateTokens(paginatedTokens);
            }
            
            // Update UI elements
            this.updateTokenCount();
            this.updatePagination();
            
        } catch (error) {
            console.error('❌ Failed to update display:', error);
        }
    }

    /**
     * Update token count display
     */
    updateTokenCount() {
        try {
            const total = this.state.tokens.length;
            const filtered = this.state.filteredTokens.length;
            
            if (this.elements.tokenCount) {
                this.elements.tokenCount.textContent = 
                    filtered !== total ? `${filtered} of ${total}` : `${total}`;
            }
            
        } catch (error) {
            console.error('❌ Failed to update token count:', error);
        }
    }

    /**
     * Update pagination controls
     */
    updatePagination() {
        try {
            if (!this.elements.pagination) return;
            
            const { currentPage, totalPages } = this.state.pagination;
            
            // Generate pagination HTML
            let paginationHtml = '';
            
            // Previous button
            paginationHtml += `
                <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                    <button class="page-link" onclick="tokenDiscoveryController.goToPage(${currentPage - 1})">
                        Previous
                    </button>
                </li>
            `;
            
            // Page numbers
            const startPage = Math.max(1, currentPage - 2);
            const endPage = Math.min(totalPages, currentPage + 2);
            
            for (let i = startPage; i <= endPage; i++) {
                paginationHtml += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <button class="page-link" onclick="tokenDiscoveryController.goToPage(${i})">
                            ${i}
                        </button>
                    </li>
                `;
            }
            
            // Next button
            paginationHtml += `
                <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                    <button class="page-link" onclick="tokenDiscoveryController.goToPage(${currentPage + 1})">
                        Next
                    </button>
                </li>
            `;
            
            this.elements.pagination.innerHTML = paginationHtml;
            
        } catch (error) {
            console.error('❌ Failed to update pagination:', error);
        }
    }

    /**
     * Update discovery status
     */
    updateDiscoveryStatus(status) {
        try {
            if (this.elements.discoveryStatus) {
                let statusText = '';
                let statusClass = '';
                
                switch (status) {
                    case 'running':
                        statusText = 'Discovering';
                        statusClass = 'text-success';
                        break;
                    case 'stopped':
                        statusText = 'Stopped';
                        statusClass = 'text-secondary';
                        break;
                    case 'offline':
                        statusText = 'Offline';
                        statusClass = 'text-danger';
                        break;
                    default:
                        statusText = 'Unknown';
                        statusClass = 'text-muted';
                }
                
                this.elements.discoveryStatus.textContent = statusText;
                this.elements.discoveryStatus.className = `discovery-status ${statusClass}`;
            }
            
        } catch (error) {
            console.error('❌ Failed to update discovery status:', error);
        }
    }

    /**
     * Update discovery controls
     */
    updateDiscoveryControls() {
        try {
            if (this.elements.startButton) {
                this.elements.startButton.disabled = this.isDiscovering;
                this.elements.startButton.textContent = this.isDiscovering ? 'Running...' : 'Start Discovery';
            }
            
            if (this.elements.pauseButton) {
                this.elements.pauseButton.disabled = !this.isDiscovering;
            }
            
        } catch (error) {
            console.error('❌ Failed to update discovery controls:', error);
        }
    }

    /**
     * Update last scan time
     */
    updateLastScanTime() {
        try {
            if (this.elements.lastUpdate) {
                const now = new Date();
                const timeString = this.app.formatters ? 
                    this.app.formatters.formatTime(now) : 
                    now.toLocaleTimeString();
                
                this.elements.lastUpdate.textContent = timeString;
            }
            
        } catch (error) {
            console.error('❌ Failed to update last scan time:', error);
        }
    }

    // Utility Methods

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Handle errors
     */
    handleError(context, error) {
        console.error(`❌ Token Discovery Controller Error [${context}]:`, error);
        
        // Show user-friendly error message
        if (this.app.showError) {
            this.app.showError(`${context}: ${error.message || 'Unknown error'}`);
        }
    }

    // Public API Methods

    /**
     * Get current controller state
     */
    getState() {
        return {
            ...this.state,
            isInitialized: this.isInitialized,
            isDiscovering: this.isDiscovering,
            config: this.config
        };
    }

    /**
     * Get filtered tokens
     */
    getFilteredTokens() {
        return [...this.state.filteredTokens];
    }

    /**
     * Get watchlist
     */
    getWatchlist() {
        return Array.from(this.state.watchlist);
    }

    /**
     * Export token data
     */
    exportTokens(format = 'json') {
        try {
            const data = {
                tokens: this.state.filteredTokens,
                filters: this.state.filters,
                exported_at: new Date().toISOString(),
                total_count: this.state.filteredTokens.length
            };
            
            if (format === 'json') {
                return JSON.stringify(data, null, 2);
            } else if (format === 'csv') {
                return this.convertToCSV(data.tokens);
            }
            
            return data;
            
        } catch (error) {
            console.error('❌ Failed to export tokens:', error);
            return null;
        }
    }

    /**
     * Convert tokens to CSV format
     */
    convertToCSV(tokens) {
        try {
            if (!tokens.length) return '';
            
            const headers = Object.keys(tokens[0]);
            const csvContent = [
                headers.join(','),
                ...tokens.map(token => 
                    headers.map(header => 
                        JSON.stringify(token[header] || '')
                    ).join(',')
                )
            ].join('\n');
            
            return csvContent;
            
        } catch (error) {
            console.error('❌ Failed to convert to CSV:', error);
            return '';
        }
    }

    /**
     * Cleanup resources
     */
    destroy() {
        try {
            console.log('🧹 Cleaning up Token Discovery Controller...');
            
            // Stop discovery
            this.stopDiscovery();
            
            // Save watchlist
            this.saveWatchlist();
            
            // Clear state
            this.state = {
                tokens: [],
                filteredTokens: [],
                watchlist: new Set(),
                filters: {},
                pagination: {},
                sorting: {}
            };
            
            this.isInitialized = false;
            
            console.log('✅ Token Discovery Controller cleaned up');
            
        } catch (error) {
            console.error('❌ Failed to cleanup Token Discovery Controller:', error);
        }
    }
}

// Export for global use
window.TokenDiscoveryController = TokenDiscoveryController;

// Create global instance for direct access
window.tokenDiscoveryController = null;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TokenDiscoveryController;
}

console.log('🔍 Token Discovery Controller module loaded successfully');