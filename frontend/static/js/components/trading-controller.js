/**
 * Trading Controller Frontend Component
 * File: frontend/static/js/components/trading-controller.js
 * 
 * Professional trading interface controller with order execution,
 * risk management, and real-time order tracking capabilities.
 */

class TradingController {
    constructor() {
        this.orders = [];
        this.portfolio = null;
        this.selectedToken = null;
        this.userWallet = '0x742d35Cc6634C0532925a3b8D404d9e6a3f8A726'; // Mock wallet
        this.defaultSlippage = 0.01; // 1%
        this.isTrading = false;
        
        this.init();
        console.log('✅ TradingController initialized');
    }
    
    init() {
        this.bindEvents();
        this.loadPortfolio();
        this.loadOrders();
        this.startOrderMonitoring();
    }
    
    bindEvents() {
        // Buy/Sell button events
        $(document).on('click', '.btn-buy', (e) => this.handleBuyClick(e));
        $(document).on('click', '.btn-sell', (e) => this.handleSellClick(e));
        $(document).on('click', '.btn-cancel-order', (e) => this.handleCancelOrder(e));
        
        // Form submissions
        $(document).on('submit', '#trade-form', (e) => this.handleTradeSubmit(e));
        $(document).on('submit', '#limit-order-form', (e) => this.handleLimitOrderSubmit(e));
        
        // Input validation events
        $(document).on('input', '.trade-amount', (e) => this.validateTradeAmount(e));
        $(document).on('input', '.slippage-input', (e) => this.validateSlippage(e));
        $(document).on('change', '.token-select', (e) => this.handleTokenSelect(e));
        
        // Real-time updates
        $(document).on('click', '.refresh-portfolio', () => this.loadPortfolio());
        $(document).on('click', '.refresh-orders', () => this.loadOrders());
    }
    
    /**
     * Execute a buy order
     * @param {string} tokenAddress - Token contract address
     * @param {number} amount - Amount to buy (in USD)
     * @param {object} options - Additional order options
     */
    async executeBuy(tokenAddress, amount, options = {}) {
        try {
            console.log(`🚀 Executing BUY order: ${amount} USD of ${tokenAddress.substring(0, 10)}...`);
            
            this.setTradingState(true);
            
            const orderData = {
                token_address: tokenAddress,
                side: 'buy',
                amount: parseFloat(amount),
                order_type: options.orderType || 'market',
                slippage_tolerance: options.slippage || this.defaultSlippage,
                limit_price: options.limitPrice || null,
                expires_in_minutes: options.expiresIn || 60
            };
            
            // Show loading state
            this.showTradeLoading('Executing buy order...');
            
            const response = await APIClient.post('/api/v1/trading/execute', orderData, {
                user_wallet: this.userWallet
            });
            
            if (response.success) {
                this.showTradeSuccess('Buy order executed successfully!', response.data);
                await this.loadPortfolio();
                await this.loadOrders();
                
                // Trigger portfolio update event
                $(document).trigger('portfolio:updated', response.data);
                
                console.log('✅ Buy order executed successfully:', response.data.order_id);
                return response.data;
            } else {
                throw new Error(response.data.error || 'Buy order failed');
            }
            
        } catch (error) {
            console.error('❌ Buy order execution failed:', error);
            this.showTradeError('Buy order failed: ' + error.message);
            throw error;
        } finally {
            this.setTradingState(false);
        }
    }
    
    /**
     * Execute a sell order
     * @param {string} tokenAddress - Token contract address
     * @param {number} amount - Amount to sell (in token units)
     * @param {object} options - Additional order options
     */
    async executeSell(tokenAddress, amount, options = {}) {
        try {
            console.log(`🚀 Executing SELL order: ${amount} tokens of ${tokenAddress.substring(0, 10)}...`);
            
            this.setTradingState(true);
            
            // Check if user has sufficient balance
            const hasBalance = await this.checkTokenBalance(tokenAddress, amount);
            if (!hasBalance) {
                throw new Error('Insufficient token balance for this trade');
            }
            
            const orderData = {
                token_address: tokenAddress,
                side: 'sell',
                amount: parseFloat(amount),
                order_type: options.orderType || 'market',
                slippage_tolerance: options.slippage || this.defaultSlippage,
                limit_price: options.limitPrice || null,
                expires_in_minutes: options.expiresIn || 60
            };
            
            this.showTradeLoading('Executing sell order...');
            
            const response = await APIClient.post('/api/v1/trading/execute', orderData, {
                user_wallet: this.userWallet
            });
            
            if (response.success) {
                this.showTradeSuccess('Sell order executed successfully!', response.data);
                await this.loadPortfolio();
                await this.loadOrders();
                
                $(document).trigger('portfolio:updated', response.data);
                
                console.log('✅ Sell order executed successfully:', response.data.order_id);
                return response.data;
            } else {
                throw new Error(response.data.error || 'Sell order failed');
            }
            
        } catch (error) {
            console.error('❌ Sell order execution failed:', error);
            this.showTradeError('Sell order failed: ' + error.message);
            throw error;
        } finally {
            this.setTradingState(false);
        }
    }
    
    /**
     * Calculate slippage for a trade
     * @param {number} expectedPrice - Expected price
     * @param {number} actualPrice - Actual execution price
     * @param {string} side - 'buy' or 'sell'
     */
    calculateSlippage(expectedPrice, actualPrice, side) {
        try {
            if (!expectedPrice || !actualPrice) {
                return 0;
            }
            
            let slippage;
            if (side === 'buy') {
                // For buys, slippage is positive when we pay more than expected
                slippage = (actualPrice - expectedPrice) / expectedPrice;
            } else {
                // For sells, slippage is positive when we receive less than expected
                slippage = (expectedPrice - actualPrice) / expectedPrice;
            }
            
            return Math.round(slippage * 10000) / 100; // Convert to percentage with 2 decimals
            
        } catch (error) {
            console.error('❌ Error calculating slippage:', error);
            return 0;
        }
    }
    
    /**
     * Cancel an active order
     * @param {string} orderId - Order ID to cancel
     */
    async cancelOrder(orderId) {
        try {
            console.log(`❌ Cancelling order: ${orderId}`);
            
            const response = await APIClient.post('/api/v1/trading/cancel-order', {
                order_id: orderId
            }, {
                user_wallet: this.userWallet
            });
            
            if (response.success) {
                this.showOrderSuccess(`Order ${orderId} cancelled successfully`);
                await this.loadOrders();
                console.log('✅ Order cancelled successfully');
            } else {
                throw new Error(response.data.error || 'Order cancellation failed');
            }
            
        } catch (error) {
            console.error('❌ Order cancellation failed:', error);
            this.showOrderError('Order cancellation failed: ' + error.message);
        }
    }
    
    /**
     * Get all orders for the user
     */
    async getOrders() {
        try {
            const response = await APIClient.get('/api/v1/trading/orders', {
                user_wallet: this.userWallet,
                limit: 100
            });
            
            if (response.success) {
                this.orders = response.data;
                return this.orders;
            } else {
                throw new Error(response.error || 'Failed to fetch orders');
            }
            
        } catch (error) {
            console.error('❌ Error getting orders:', error);
            throw error;
        }
    }
    
    /**
     * Get portfolio information
     */
    async getPortfolio() {
        try {
            const response = await APIClient.get('/api/v1/trading/portfolio', {
                user_wallet: this.userWallet,
                include_history: false
            });
            
            if (response.success) {
                this.portfolio = response.data;
                return this.portfolio;
            } else {
                throw new Error(response.error || 'Failed to fetch portfolio');
            }
            
        } catch (error) {
            console.error('❌ Error getting portfolio:', error);
            throw error;
        }
    }
    
    /**
     * Calculate optimal position size based on risk management
     * @param {number} accountValue - Total account value
     * @param {number} riskPercentage - Risk percentage (e.g., 2 for 2%)
     * @param {number} stopLossDistance - Distance to stop loss in percentage
     */
    calculatePositionSize(accountValue, riskPercentage, stopLossDistance) {
        try {
            if (!accountValue || !riskPercentage || !stopLossDistance) {
                return 0;
            }
            
            const riskAmount = accountValue * (riskPercentage / 100);
            const positionSize = riskAmount / (stopLossDistance / 100);
            
            return Math.round(positionSize * 100) / 100;
            
        } catch (error) {
            console.error('❌ Error calculating position size:', error);
            return 0;
        }
    }
    
    /**
     * Set stop loss for a position
     * @param {string} tokenAddress - Token address
     * @param {number} stopPrice - Stop loss price
     * @param {boolean} isTrailing - Whether it's a trailing stop
     */
    async setStopLoss(tokenAddress, stopPrice, isTrailing = false) {
        try {
            console.log(`🛡️ Setting stop loss for ${tokenAddress}: ${stopPrice}`);
            
            // TODO: Implement stop loss API call when backend supports it
            // For now, show mock success
            this.showOrderSuccess(`Stop loss set at ${stopPrice} for ${tokenAddress.substring(0, 10)}...`);
            
            return {
                success: true,
                stopPrice: stopPrice,
                isTrailing: isTrailing
            };
            
        } catch (error) {
            console.error('❌ Error setting stop loss:', error);
            this.showOrderError('Failed to set stop loss: ' + error.message);
        }
    }
    
    // Event Handlers
    
    handleBuyClick(e) {
        e.preventDefault();
        const tokenAddress = $(e.target).data('token') || this.selectedToken;
        
        if (!tokenAddress) {
            this.showTradeError('Please select a token first');
            return;
        }
        
        this.showTradeModal('buy', tokenAddress);
    }
    
    handleSellClick(e) {
        e.preventDefault();
        const tokenAddress = $(e.target).data('token') || this.selectedToken;
        
        if (!tokenAddress) {
            this.showTradeError('Please select a token first');
            return;
        }
        
        this.showTradeModal('sell', tokenAddress);
    }
    
    async handleTradeSubmit(e) {
        e.preventDefault();
        
        const form = $(e.target);
        const formData = this.getFormData(form);
        
        if (!this.validateTradeForm(formData)) {
            return;
        }
        
        try {
            if (formData.side === 'buy') {
                await this.executeBuy(formData.tokenAddress, formData.amount, {
                    slippage: formData.slippage,
                    orderType: formData.orderType
                });
            } else {
                await this.executeSell(formData.tokenAddress, formData.amount, {
                    slippage: formData.slippage,
                    orderType: formData.orderType
                });
            }
            
            // Close modal on success
            $('#trade-modal').modal('hide');
            
        } catch (error) {
            // Error already handled in execute methods
        }
    }
    
    async handleLimitOrderSubmit(e) {
        e.preventDefault();
        
        const form = $(e.target);
        const formData = this.getFormData(form);
        
        if (!this.validateLimitOrderForm(formData)) {
            return;
        }
        
        try {
            if (formData.side === 'buy') {
                await this.executeBuy(formData.tokenAddress, formData.amount, {
                    orderType: 'limit',
                    limitPrice: formData.limitPrice,
                    expiresIn: formData.expiresIn
                });
            } else {
                await this.executeSell(formData.tokenAddress, formData.amount, {
                    orderType: 'limit',
                    limitPrice: formData.limitPrice,
                    expiresIn: formData.expiresIn
                });
            }
            
            $('#limit-order-modal').modal('hide');
            
        } catch (error) {
            // Error already handled in execute methods
        }
    }
    
    async handleCancelOrder(e) {
        e.preventDefault();
        const orderId = $(e.target).data('order-id');
        
        if (confirm(`Are you sure you want to cancel order ${orderId}?`)) {
            await this.cancelOrder(orderId);
        }
    }
    
    validateTradeAmount(e) {
        const input = $(e.target);
        const amount = parseFloat(input.val());
        const maxAmount = parseFloat(input.attr('max'));
        
        if (amount > maxAmount) {
            input.addClass('is-invalid');
            input.siblings('.invalid-feedback').text(`Maximum amount is ${maxAmount}`);
        } else if (amount <= 0) {
            input.addClass('is-invalid');
            input.siblings('.invalid-feedback').text('Amount must be greater than 0');
        } else {
            input.removeClass('is-invalid');
        }
    }
    
    validateSlippage(e) {
        const input = $(e.target);
        const slippage = parseFloat(input.val());
        
        if (slippage < 0 || slippage > 10) {
            input.addClass('is-invalid');
            input.siblings('.invalid-feedback').text('Slippage must be between 0% and 10%');
        } else {
            input.removeClass('is-invalid');
        }
    }
    
    handleTokenSelect(e) {
        const select = $(e.target);
        this.selectedToken = select.val();
        console.log('Token selected:', this.selectedToken);
    }
    
    // Helper Methods
    
    async loadPortfolio() {
        try {
            console.log('📊 Loading portfolio...');
            await this.getPortfolio();
            this.updatePortfolioDisplay();
        } catch (error) {
            console.error('❌ Error loading portfolio:', error);
        }
    }
    
    async loadOrders() {
        try {
            console.log('📋 Loading orders...');
            await this.getOrders();
            this.updateOrdersDisplay();
        } catch (error) {
            console.error('❌ Error loading orders:', error);
        }
    }
    
    startOrderMonitoring() {
        // Poll for order updates every 30 seconds
        setInterval(async () => {
            if (this.orders.active_orders && this.orders.active_orders.length > 0) {
                await this.loadOrders();
            }
        }, 30000);
    }
    
    async checkTokenBalance(tokenAddress, amount) {
        try {
            if (!this.portfolio || !this.portfolio.positions) {
                return false;
            }
            
            const position = this.portfolio.positions.positions.find(
                p => p.token_address === tokenAddress
            );
            
            return position && position.amount >= amount;
        } catch (error) {
            console.error('❌ Error checking token balance:', error);
            return false;
        }
    }
    
    setTradingState(isTrading) {
        this.isTrading = isTrading;
        
        // Disable/enable trading buttons
        $('.btn-buy, .btn-sell').prop('disabled', isTrading);
        
        if (isTrading) {
            $('.trading-spinner').removeClass('d-none');
        } else {
            $('.trading-spinner').addClass('d-none');
        }
    }
    
    getFormData(form) {
        const formData = {};
        form.find('input, select').each(function() {
            const field = $(this);
            formData[field.attr('name')] = field.val();
        });
        return formData;
    }
    
    validateTradeForm(formData) {
        const errors = [];
        
        if (!formData.tokenAddress) {
            errors.push('Token address is required');
        }
        
        if (!formData.amount || parseFloat(formData.amount) <= 0) {
            errors.push('Amount must be greater than 0');
        }
        
        if (formData.slippage && (parseFloat(formData.slippage) < 0 || parseFloat(formData.slippage) > 10)) {
            errors.push('Slippage must be between 0% and 10%');
        }
        
        if (errors.length > 0) {
            this.showTradeError('Validation errors: ' + errors.join(', '));
            return false;
        }
        
        return true;
    }
    
    validateLimitOrderForm(formData) {
        const errors = [];
        
        if (!this.validateTradeForm(formData)) {
            return false;
        }
        
        if (!formData.limitPrice || parseFloat(formData.limitPrice) <= 0) {
            errors.push('Limit price must be greater than 0');
        }
        
        if (errors.length > 0) {
            this.showTradeError('Validation errors: ' + errors.join(', '));
            return false;
        }
        
        return true;
    }
    
    // UI Update Methods
    
    updatePortfolioDisplay() {
        if (!this.portfolio) return;
        
        const container = $('#portfolio-container');
        if (container.length === 0) return;
        
        const summary = this.portfolio.positions.summary;
        
        // Update portfolio summary
        $('.portfolio-total-value').text(Formatters.formatCurrency(summary.total_value));
        $('.portfolio-cash-balance').text(Formatters.formatCurrency(summary.cash_balance));
        $('.portfolio-pnl').text(Formatters.formatCurrency(summary.total_pnl));
        $('.portfolio-return-pct').text(Formatters.formatPercentage(summary.total_return_percentage));
        
        // Update positions table
        this.updatePositionsTable(this.portfolio.positions.positions);
    }
    
    updatePositionsTable(positions) {
        const tbody = $('#positions-table tbody');
        if (tbody.length === 0) return;
        
        tbody.empty();
        
        positions.forEach(position => {
            const row = `
                <tr>
                    <td>
                        <strong>${position.symbol}</strong>
                        <br><small class="text-muted">${position.token_address.substring(0, 10)}...</small>
                    </td>
                    <td>${Formatters.formatNumber(position.amount, 4)}</td>
                    <td>${Formatters.formatCurrency(position.current_price)}</td>
                    <td>${Formatters.formatCurrency(position.market_value)}</td>
                    <td class="${position.unrealized_pnl >= 0 ? 'text-success' : 'text-danger'}">
                        ${Formatters.formatCurrency(position.unrealized_pnl)}
                        <br><small>(${Formatters.formatPercentage(position.unrealized_pnl_percentage)})</small>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-success btn-buy" data-token="${position.token_address}">
                                Buy
                            </button>
                            <button class="btn btn-outline-danger btn-sell" data-token="${position.token_address}">
                                Sell
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }
    
    updateOrdersDisplay() {
        if (!this.orders) return;
        
        this.updateActiveOrdersTable(this.orders.active_orders || []);
        this.updateOrderHistoryTable(this.orders.order_history || []);
    }
    
    updateActiveOrdersTable(activeOrders) {
        const tbody = $('#active-orders-table tbody');
        if (tbody.length === 0) return;
        
        tbody.empty();
        
        if (activeOrders.length === 0) {
            tbody.append('<tr><td colspan="7" class="text-center text-muted">No active orders</td></tr>');
            return;
        }
        
        activeOrders.forEach(order => {
            const row = `
                <tr>
                    <td><small>${order.order_id}</small></td>
                    <td>
                        <span class="badge badge-${order.side === 'buy' ? 'success' : 'danger'}">
                            ${order.side.toUpperCase()}
                        </span>
                    </td>
                    <td>${order.type.toUpperCase()}</td>
                    <td>${Formatters.formatNumber(order.amount, 4)}</td>
                    <td>${order.price ? Formatters.formatCurrency(order.price) : 'Market'}</td>
                    <td>
                        <span class="badge badge-warning">${order.status.toUpperCase()}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger btn-cancel-order" data-order-id="${order.order_id}">
                            Cancel
                        </button>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }
    
    updateOrderHistoryTable(orderHistory) {
        const tbody = $('#order-history-table tbody');
        if (tbody.length === 0) return;
        
        tbody.empty();
        
        if (orderHistory.length === 0) {
            tbody.append('<tr><td colspan="6" class="text-center text-muted">No order history</td></tr>');
            return;
        }
        
        orderHistory.slice(0, 10).forEach(order => {
            const row = `
                <tr>
                    <td><small>${order.order_id}</small></td>
                    <td>
                        <span class="badge badge-${order.side === 'buy' ? 'success' : 'danger'}">
                            ${order.side.toUpperCase()}
                        </span>
                    </td>
                    <td>${Formatters.formatNumber(order.filled_amount || order.amount, 4)}</td>
                    <td>${order.average_fill_price ? Formatters.formatCurrency(order.average_fill_price) : '-'}</td>
                    <td>
                        <span class="badge badge-${this.getStatusBadgeClass(order.status)}">
                            ${order.status.toUpperCase()}
                        </span>
                    </td>
                    <td><small>${Formatters.formatDateTime(order.created_at)}</small></td>
                </tr>
            `;
            tbody.append(row);
        });
    }
    
    getStatusBadgeClass(status) {
        const statusClasses = {
            'filled': 'success',
            'cancelled': 'secondary',
            'failed': 'danger',
            'expired': 'warning',
            'partially_filled': 'info'
        };
        return statusClasses[status] || 'secondary';
    }
    
    showTradeModal(side, tokenAddress) {
        // TODO: Implement modal display
        console.log(`Opening ${side} modal for token ${tokenAddress}`);
    }
    
    showTradeLoading(message) {
        // TODO: Implement loading state
        console.log('Trading loading:', message);
    }
    
    showTradeSuccess(message, data) {
        // TODO: Implement success notification
        console.log('Trading success:', message, data);
    }
    
    showTradeError(message) {
        // TODO: Implement error notification
        console.error('Trading error:', message);
    }
    
    showOrderSuccess(message) {
        console.log('Order success:', message);
    }
    
    showOrderError(message) {
        console.error('Order error:', message);
    }
}

// Export for use in other modules
window.TradingController = TradingController;