/**
 * Snipe Button Frontend Integration - Phase 4D
 * File: frontend/static/js/snipe-integration.js
 * Class: SnipeButtonController
 * Methods: handleSnipeClick, validateTrade, executeSnipe, monitorExecution
 * 
 * Handles frontend snipe button interactions and connects them to the backend
 * snipe trading API with real-time status updates and user feedback.
 */

class SnipeButtonController {
    constructor() {
        this.apiBaseUrl = '/api/v1/snipe';
        this.activeSnipes = new Map();
        this.websocketConnections = new Map();
        this.notificationManager = null;
        
        // Snipe configuration defaults
        this.defaultConfig = {
            slippageTolerance: 0.02,        // 2%
            deadlineSeconds: 300,           // 5 minutes
            gasMultiplier: 1.2,             // 20% above estimate
            maxGasPrice: 50                 // 50 GWEI
        };
        
        // UI elements cache
        this.elements = {
            snipeButtons: null,
            statusModal: null,
            confirmationModal: null,
            progressIndicator: null
        };
        
        this.isInitialized = false;
        console.log('🎯 Snipe Button Controller initialized');
    }
    
    /**
     * Initialize the snipe button controller
     */
    async init() {
        try {
            if (this.isInitialized) {
                console.warn('⚠️ Snipe controller already initialized');
                return;
            }
            
            // Cache DOM elements
            this.cacheElements();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize notification manager
            await this.initializeNotifications();
            
            // Setup WebSocket handlers
            this.setupWebSocketHandlers();
            
            // Load user preferences
            await this.loadUserPreferences();
            
            this.isInitialized = true;
            console.log('✅ Snipe Button Controller initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize snipe controller:', error);
            throw error;
        }
    }
    
    /**
     * Cache frequently used DOM elements
     */
    cacheElements() {
        this.elements.snipeButtons = document.querySelectorAll('.snipe-button');
        this.elements.statusModal = document.getElementById('snipe-status-modal');
        this.elements.confirmationModal = document.getElementById('snipe-confirmation-modal');
        this.elements.progressIndicator = document.getElementById('snipe-progress');
        
        console.log(`📋 Cached ${this.elements.snipeButtons.length} snipe buttons`);
    }
    
    /**
     * Setup event listeners for snipe buttons
     */
    setupEventListeners() {
        // Snipe button click handlers
        this.elements.snipeButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                this.handleSnipeClick(event);
            });
            
            // Add hover effects
            button.addEventListener('mouseenter', (event) => {
                this.showQuickPreview(event.target);
            });
            
            button.addEventListener('mouseleave', (event) => {
                this.hideQuickPreview(event.target);
            });
        });
        
        // Modal event listeners
        if (this.elements.confirmationModal) {
            const confirmButton = this.elements.confirmationModal.querySelector('.confirm-snipe');
            const cancelButton = this.elements.confirmationModal.querySelector('.cancel-snipe');
            
            if (confirmButton) {
                confirmButton.addEventListener('click', () => {
                    this.confirmSnipeExecution();
                });
            }
            
            if (cancelButton) {
                cancelButton.addEventListener('click', () => {
                    this.cancelSnipeExecution();
                });
            }
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });
        
        console.log('✅ Event listeners setup complete');
    }
    
    /**
     * Handle snipe button click
     */
    async handleSnipeClick(event) {
        try {
            event.preventDefault();
            const button = event.target;
            
            // Prevent double clicks
            if (button.disabled || button.classList.contains('snipe-processing')) {
                return;
            }
            
            // Extract token data from button attributes
            const tokenData = this.extractTokenData(button);
            if (!tokenData) {
                this.showError('Invalid token data');
                return;
            }
            
            console.log('🎯 Snipe button clicked:', tokenData.symbol);
            
            // Show loading state
            this.setButtonState(button, 'validating');
            
            // Step 1: Validate the trade first
            const validation = await this.validateTrade(tokenData);
            
            if (!validation.success) {
                this.setButtonState(button, 'error');
                this.showValidationErrors(validation.errors);
                return;
            }
            
            // Step 2: Check risk level and show confirmation if needed
            if (validation.data.risk_level === 'HIGH' || validation.data.risk_level === 'EXTREME') {
                await this.showRiskConfirmation(tokenData, validation.data);
                return;
            }
            
            // Step 3: Execute the snipe
            await this.executeSnipe(tokenData, button);
            
        } catch (error) {
            console.error('❌ Snipe button click error:', error);
            this.showError(`Snipe failed: ${error.message}`);
            this.setButtonState(event.target, 'error');
        }
    }
    
    /**
     * Extract token data from button attributes
     */
    extractTokenData(button) {
        try {
            const row = button.closest('tr') || button.closest('.token-card');
            if (!row) return null;
            
            return {
                tokenAddress: button.dataset.tokenAddress || row.dataset.tokenAddress,
                symbol: button.dataset.symbol || row.querySelector('.token-symbol')?.textContent,
                network: button.dataset.network || row.dataset.network || 'ethereum',
                dexProtocol: button.dataset.dex || row.dataset.dex || 'uniswap_v2',
                snipeType: button.dataset.snipeType || 'buy_snipe',
                suggestedAmount: button.dataset.amount || row.dataset.amount || '0.1',
                price: row.querySelector('.token-price')?.textContent,
                marketCap: row.querySelector('.market-cap')?.textContent,
                liquidity: row.querySelector('.liquidity')?.textContent
            };
        } catch (error) {
            console.error('❌ Error extracting token data:', error);
            return null;
        }
    }
    
    /**
     * Validate trade before execution
     */
    async validateTrade(tokenData) {
        try {
            console.log('🔍 Validating trade for:', tokenData.symbol);
            
            // Get wallet connection
            const walletConnectionId = await this.getActiveWalletConnection();
            if (!walletConnectionId) {
                throw new Error('No wallet connected');
            }
            
            // Prepare validation request
            const validationRequest = {
                snipe_request: {
                    snipe_type: tokenData.snipeType,
                    token_address: tokenData.tokenAddress,
                    token_symbol: tokenData.symbol,
                    network: tokenData.network,
                    dex_protocol: tokenData.dexProtocol,
                    amount_in: parseFloat(tokenData.suggestedAmount),
                    slippage_tolerance: this.defaultConfig.slippageTolerance,
                    wallet_connection_id: walletConnectionId,
                    deadline_seconds: this.defaultConfig.deadlineSeconds,
                    user_confirmation: false
                }
            };
            
            // Send validation request
            const response = await fetch(`${this.apiBaseUrl}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(validationRequest)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Validation failed');
            }
            
            const validationResult = await response.json();
            console.log('✅ Validation complete:', validationResult);
            
            return {
                success: validationResult.is_valid,
                data: validationResult,
                errors: validationResult.validation_errors || []
            };
            
        } catch (error) {
            console.error('❌ Trade validation error:', error);
            return {
                success: false,
                data: null,
                errors: [error.message]
            };
        }
    }
    
    /**
     * Execute the snipe trade
     */
    async executeSnipe(tokenData, button) {
        try {
            console.log('⚡ Executing snipe for:', tokenData.symbol);
            
            // Set button to executing state
            this.setButtonState(button, 'executing');
            
            // Get wallet connection
            const walletConnectionId = await this.getActiveWalletConnection();
            
            // Prepare execution request
            const executionRequest = {
                snipe_type: tokenData.snipeType,
                token_address: tokenData.tokenAddress,
                token_symbol: tokenData.symbol,
                network: tokenData.network,
                dex_protocol: tokenData.dexProtocol,
                amount_in: parseFloat(tokenData.suggestedAmount),
                slippage_tolerance: this.defaultConfig.slippageTolerance,
                wallet_connection_id: walletConnectionId,
                deadline_seconds: this.defaultConfig.deadlineSeconds,
                user_confirmation: false
            };
            
            // Execute the snipe
            const response = await fetch(`${this.apiBaseUrl}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(executionRequest)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Execution failed');
            }
            
            const executionResult = await response.json();
            console.log('✅ Snipe execution started:', executionResult);
            
            // Store active snipe
            this.activeSnipes.set(executionResult.request_id, {
                tokenData,
                executionResult,
                button,
                startTime: Date.now()
            });
            
            // Start monitoring
            await this.monitorExecution(executionResult.request_id);
            
            // Show success notification
            this.showNotification(
                `Snipe executed for ${tokenData.symbol}`,
                'success',
                { action: 'View Status', callback: () => this.showExecutionStatus(executionResult.execution_id) }
            );
            
        } catch (error) {
            console.error('❌ Snipe execution error:', error);
            this.showError(`Execution failed: ${error.message}`);
            this.setButtonState(button, 'error');
        }
    }
    
    /**
     * Monitor snipe execution via WebSocket
     */
    async monitorExecution(requestId) {
        try {
            console.log('📊 Starting execution monitoring for:', requestId);
            
            const wsUrl = `ws://${window.location.host}${this.apiBaseUrl}/ws/${requestId}`;
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('🔌 WebSocket connected for snipe monitoring');
                this.websocketConnections.set(requestId, ws);
            };
            
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(requestId, message);
            };
            
            ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.handleExecutionError(requestId, 'WebSocket connection failed');
            };
            
            ws.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.websocketConnections.delete(requestId);
            };
            
        } catch (error) {
            console.error('❌ Error starting execution monitoring:', error);
        }
    }
    
    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(requestId, message) {
        console.log('📨 WebSocket message:', message);
        
        const activeSnipe = this.activeSnipes.get(requestId);
        if (!activeSnipe) return;
        
        switch (message.type) {
            case 'connection_established':
                this.updateExecutionProgress(requestId, 'Connected', 10);
                break;
                
            case 'progress_update':
                this.updateExecutionProgress(requestId, 'Processing', 50);
                break;
                
            case 'execution_complete':
                this.handleExecutionComplete(requestId, message);
                break;
                
            case 'snipe_not_found':
                this.handleExecutionError(requestId, 'Snipe request not found');
                break;
                
            case 'error':
                this.handleExecutionError(requestId, message.error);
                break;
        }
    }
    
    /**
     * Handle execution completion
     */
    handleExecutionComplete(requestId, message) {
        const activeSnipe = this.activeSnipes.get(requestId);
        if (!activeSnipe) return;
        
        console.log('✅ Execution complete:', message);
        
        if (message.status === 'completed') {
            this.setButtonState(activeSnipe.button, 'success');
            this.updateExecutionProgress(requestId, 'Completed', 100);
            
            this.showNotification(
                `Snipe successful for ${activeSnipe.tokenData.symbol}!`,
                'success',
                {
                    action: 'View Transaction',
                    callback: () => this.openTransaction(message.transaction_hash)
                }
            );
        } else {
            this.setButtonState(activeSnipe.button, 'error');
            this.handleExecutionError(requestId, message.error_message || 'Execution failed');
        }
        
        // Cleanup
        setTimeout(() => {
            this.cleanupSnipe(requestId);
        }, 30000); // Keep for 30 seconds
    }
    
    /**
     * Handle execution error
     */
    handleExecutionError(requestId, errorMessage) {
        const activeSnipe = this.activeSnipes.get(requestId);
        if (!activeSnipe) return;
        
        console.error('❌ Execution error:', errorMessage);
        
        this.setButtonState(activeSnipe.button, 'error');
        this.showError(`Snipe failed: ${errorMessage}`);
        
        this.cleanupSnipe(requestId);
    }
    
    /**
     * Update execution progress
     */
    updateExecutionProgress(requestId, status, progress) {
        const activeSnipe = this.activeSnipes.get(requestId);
        if (!activeSnipe) return;
        
        // Update button text
        const button = activeSnipe.button;
        const originalText = button.dataset.originalText || button.textContent;
        button.textContent = `${status} (${progress}%)`;
        
        // Update progress indicator if available
        if (this.elements.progressIndicator) {
            this.elements.progressIndicator.style.width = `${progress}%`;
            this.elements.progressIndicator.textContent = status;
        }
        
        console.log(`📊 Progress update: ${status} (${progress}%)`);
    }
    
    /**
     * Set button state
     */
    setButtonState(button, state) {
        if (!button) return;
        
        // Store original text if not already stored
        if (!button.dataset.originalText) {
            button.dataset.originalText = button.textContent;
        }
        
        // Reset classes
        button.classList.remove('snipe-validating', 'snipe-executing', 'snipe-success', 'snipe-error', 'snipe-processing');
        button.disabled = false;
        
        switch (state) {
            case 'validating':
                button.classList.add('snipe-validating', 'snipe-processing');
                button.disabled = true;
                button.textContent = 'Validating...';
                break;
                
            case 'executing':
                button.classList.add('snipe-executing', 'snipe-processing');
                button.disabled = true;
                button.textContent = 'Executing...';
                break;
                
            case 'success':
                button.classList.add('snipe-success');
                button.textContent = 'Success!';
                setTimeout(() => {
                    button.textContent = button.dataset.originalText;
                    button.classList.remove('snipe-success');
                }, 3000);
                break;
                
            case 'error':
                button.classList.add('snipe-error');
                button.textContent = 'Failed';
                setTimeout(() => {
                    button.textContent = button.dataset.originalText;
                    button.classList.remove('snipe-error');
                }, 3000);
                break;
                
            default:
                button.textContent = button.dataset.originalText;
        }
    }
    
    /**
     * Show risk confirmation dialog
     */
    async showRiskConfirmation(tokenData, validationData) {
        return new Promise((resolve) => {
            if (!this.elements.confirmationModal) {
                this.showError('Confirmation modal not found');
                resolve(false);
                return;
            }
            
            // Populate confirmation modal
            const modal = this.elements.confirmationModal;
            modal.querySelector('.token-symbol').textContent = tokenData.symbol;
            modal.querySelector('.risk-level').textContent = validationData.risk_level;
            modal.querySelector('.risk-score').textContent = (validationData.risk_score * 100).toFixed(1) + '%';
            modal.querySelector('.confidence-score').textContent = (validationData.confidence_score * 100).toFixed(1) + '%';
            
            // Show warnings
            const warningsList = modal.querySelector('.validation-warnings');
            warningsList.innerHTML = '';
            validationData.validation_warnings.forEach(warning => {
                const li = document.createElement('li');
                li.textContent = warning;
                warningsList.appendChild(li);
            });
            
            // Show modal
            modal.style.display = 'block';
            modal.classList.add('show');
            
            // Store resolve function for confirmation handlers
            this.pendingConfirmation = { resolve, tokenData };
        });
    }
    
    /**
     * Confirm snipe execution
     */
    async confirmSnipeExecution() {
        if (!this.pendingConfirmation) return;
        
        const { resolve, tokenData } = this.pendingConfirmation;
        this.hideConfirmationModal();
        
        try {
            const button = document.querySelector(`[data-token-address="${tokenData.tokenAddress}"] .snipe-button`);
            await this.executeSnipe(tokenData, button);
            resolve(true);
        } catch (error) {
            console.error('❌ Confirmed execution failed:', error);
            resolve(false);
        }
        
        this.pendingConfirmation = null;
    }
    
    /**
     * Cancel snipe execution
     */
    cancelSnipeExecution() {
        if (!this.pendingConfirmation) return;
        
        this.hideConfirmationModal();
        this.pendingConfirmation.resolve(false);
        this.pendingConfirmation = null;
    }
    
    /**
     * Hide confirmation modal
     */
    hideConfirmationModal() {
        if (this.elements.confirmationModal) {
            this.elements.confirmationModal.style.display = 'none';
            this.elements.confirmationModal.classList.remove('show');
        }
    }
    
    /**
     * Get active wallet connection
     */
    async getActiveWalletConnection() {
        try {
            // This would integrate with the wallet connection system
            // For now, return a mock connection ID
            const walletConnections = await fetch('/api/v1/wallet/connections');
            if (!walletConnections.ok) {
                throw new Error('No wallet connections available');
            }
            
            const connections = await walletConnections.json();
            const activeConnection = Object.keys(connections)[0];
            
            if (!activeConnection) {
                throw new Error('No active wallet connection');
            }
            
            return activeConnection;
            
        } catch (error) {
            console.error('❌ Error getting wallet connection:', error);
            throw new Error('Please connect your wallet first');
        }
    }
    
    /**
     * Show quick preview on hover
     */
    showQuickPreview(button) {
        const tokenData = this.extractTokenData(button);
        if (!tokenData) return;
        
        // Create or update preview tooltip
        let preview = document.getElementById('snipe-preview');
        if (!preview) {
            preview = document.createElement('div');
            preview.id = 'snipe-preview';
            preview.className = 'snipe-preview-tooltip';
            document.body.appendChild(preview);
        }
        
        preview.innerHTML = `
            <div class="preview-header">${tokenData.symbol} Snipe Preview</div>
            <div class="preview-details">
                <div>Amount: ${tokenData.suggestedAmount} ETH</div>
                <div>Network: ${tokenData.network}</div>
                <div>DEX: ${tokenData.dexProtocol}</div>
                <div>Slippage: ${(this.defaultConfig.slippageTolerance * 100).toFixed(1)}%</div>
            </div>
        `;
        
        // Position tooltip
        const rect = button.getBoundingClientRect();
        preview.style.left = rect.left + 'px';
        preview.style.top = (rect.bottom + 10) + 'px';
        preview.style.display = 'block';
    }
    
    /**
     * Hide quick preview
     */
    hideQuickPreview(button) {
        const preview = document.getElementById('snipe-preview');
        if (preview) {
            preview.style.display = 'none';
        }
    }
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(event) {
        // ESC to cancel any pending operations
        if (event.key === 'Escape') {
            if (this.pendingConfirmation) {
                this.cancelSnipeExecution();
            }
            this.hideQuickPreview();
        }
        
        // ENTER to confirm pending operations
        if (event.key === 'Enter' && this.pendingConfirmation) {
            this.confirmSnipeExecution();
        }
    }
    
    /**
     * Initialize notification system
     */
    async initializeNotifications() {
        // This would integrate with the main notification system
        this.notificationManager = {
            show: (message, type, options) => {
                console.log(`🔔 ${type.toUpperCase()}: ${message}`);
                
                // Create simple notification
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.innerHTML = `
                    <div class="notification-content">
                        <span class="notification-message">${message}</span>
                        ${options?.action ? `<button class="notification-action">${options.action}</button>` : ''}
                    </div>
                `;
                
                if (options?.action && options?.callback) {
                    notification.querySelector('.notification-action').addEventListener('click', options.callback);
                }
                
                document.body.appendChild(notification);
                
                // Auto-remove after 5 seconds
                setTimeout(() => {
                    notification.remove();
                }, 5000);
            }
        };
    }
    
    /**
     * Setup WebSocket handlers
     */
    setupWebSocketHandlers() {
        // Global WebSocket error handler
        window.addEventListener('beforeunload', () => {
            this.websocketConnections.forEach(ws => {
                ws.close();
            });
        });
    }
    
    /**
     * Load user preferences
     */
    async loadUserPreferences() {
        try {
            const saved = localStorage.getItem('snipe-preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                Object.assign(this.defaultConfig, preferences);
                console.log('✅ Loaded user preferences:', preferences);
            }
        } catch (error) {
            console.warn('⚠️ Failed to load user preferences:', error);
        }
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info', options = {}) {
        if (this.notificationManager) {
            this.notificationManager.show(message, type, options);
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    /**
     * Show validation errors
     */
    showValidationErrors(errors) {
        if (errors.length === 0) return;
        
        const message = `Validation failed: ${errors.join(', ')}`;
        this.showError(message);
    }
    
    /**
     * Show execution status modal
     */
    showExecutionStatus(executionId) {
        // This would open a detailed status modal
        console.log('📊 Show execution status for:', executionId);
    }
    
    /**
     * Open transaction in block explorer
     */
    openTransaction(transactionHash) {
        if (!transactionHash) return;
        
        // Open in new tab - this would use the appropriate explorer for the network
        const explorerUrl = `https://etherscan.io/tx/${transactionHash}`;
        window.open(explorerUrl, '_blank');
    }
    
    /**
     * Cleanup completed snipe
     */
    cleanupSnipe(requestId) {
        // Close WebSocket connection
        const ws = this.websocketConnections.get(requestId);
        if (ws) {
            ws.close();
            this.websocketConnections.delete(requestId);
        }
        
        // Remove from active snipes
        this.activeSnipes.delete(requestId);
        
        console.log('🧹 Cleaned up snipe:', requestId);
    }
    
    /**
     * Get active snipes count
     */
    getActiveSnipesCount() {
        return this.activeSnipes.size;
    }
    
    /**
     * Get snipe statistics
     */
    async getSnipeStatistics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/stats`);
            if (!response.ok) throw new Error('Failed to fetch stats');
            
            return await response.json();
        } catch (error) {
            console.error('❌ Error fetching snipe statistics:', error);
            return null;
        }
    }
}

// Global instance
window.snipeController = new SnipeButtonController();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.snipeController.init();
    });
} else {
    window.snipeController.init();
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SnipeButtonController;
}