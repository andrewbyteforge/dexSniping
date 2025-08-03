/**
 * Multi-DEX Price Comparison Component
 * File: frontend/static/js/components/dex-comparison.js
 * 
 * Professional multi-DEX price aggregation and arbitrage detection.
 * Provides optimal routing and cross-platform trading capabilities.
 */

class DEXComparison {
    constructor() {
        this.dexes = new Map();
        this.priceData = new Map(); // token_address -> dex_prices
        this.arbitrageOpportunities = new Map();
        this.updateInterval = null;
        this.isUpdating = false;
        
        // Supported DEX configurations
        this.supportedDEXes = {
            uniswap_v2: {
                name: 'Uniswap V2',
                icon: '🦄',
                color: '#ff007a',
                chain: 'ethereum',
                fees: 0.003 // 0.3%
            },
            uniswap_v3: {
                name: 'Uniswap V3',
                icon: '🦄',
                color: '#ff007a',
                chain: 'ethereum',
                fees: 0.0005 // 0.05% (can vary)
            },
            sushiswap: {
                name: 'SushiSwap',
                icon: '🍣',
                color: '#fa52a0',
                chain: 'ethereum',
                fees: 0.003
            },
            pancakeswap: {
                name: 'PancakeSwap',
                icon: '🥞',
                color: '#1fc7d4',
                chain: 'bsc',
                fees: 0.0025
            },
            curve: {
                name: 'Curve',
                icon: '⚡',
                color: '#40e0d0',
                chain: 'ethereum',
                fees: 0.0004
            },
            balancer: {
                name: 'Balancer',
                icon: '⚖️',
                color: '#1e1e1e',
                chain: 'ethereum',
                fees: 0.0005
            }
        };

        this.init();
        console.log('✅ DEXComparison initialized');
    }

    /**
     * Initialize DEX comparison system
     */
    async init() {
        try {
            await this.loadDEXConfigurations();
            this.bindEvents();
            this.startPriceAggregation();
            
        } catch (error) {
            console.error('Error initializing DEXComparison:', error);
        }
    }

    /**
     * Load DEX configurations and initialize connections
     */
    async loadDEXConfigurations() {
        try {
            for (const [dexId, config] of Object.entries(this.supportedDEXes)) {
                this.dexes.set(dexId, {
                    ...config,
                    isActive: true,
                    lastUpdate: null,
                    errorCount: 0,
                    priceCount: 0
                });
            }

            console.log(`✅ Loaded ${this.dexes.size} DEX configurations`);
        } catch (error) {
            console.error('Error loading DEX configurations:', error);
        }
    }

    /**
     * Aggregate prices from multiple DEXs
     * Method: aggregatePrices()
     */
    async aggregatePrices(tokenAddress) {
        try {
            if (this.isUpdating) return;
            this.isUpdating = true;

            const promises = Array.from(this.dexes.keys()).map(dexId => 
                this.fetchDEXPrice(dexId, tokenAddress)
            );

            const results = await Promise.allSettled(promises);
            const prices = new Map();

            results.forEach((result, index) => {
                const dexId = Array.from(this.dexes.keys())[index];
                
                if (result.status === 'fulfilled' && result.value) {
                    prices.set(dexId, result.value);
                    this.updateDEXStatus(dexId, 'success');
                } else {
                    this.updateDEXStatus(dexId, 'error', result.reason);
                }
            });

            // Store aggregated prices
            this.priceData.set(tokenAddress, prices);

            // Find best prices and arbitrage opportunities
            const analysis = this.analyzePrices(tokenAddress, prices);
            
            // Update UI
            this.updatePriceComparisonDisplay(tokenAddress, prices, analysis);

            return {
                prices,
                bestBuy: analysis.bestBuy,
                bestSell: analysis.bestSell,
                arbitrage: analysis.arbitrage
            };

        } catch (error) {
            console.error('Error aggregating prices:', error);
            return null;
        } finally {
            this.isUpdating = false;
        }
    }

    /**
     * Fetch price from specific DEX
     */
    async fetchDEXPrice(dexId, tokenAddress) {
        try {
            const response = await fetch(`/api/v1/dex/${dexId}/price`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token_address: tokenAddress,
                    quote_token: 'USDC' // Default quote token
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            return {
                price: parseFloat(data.price),
                liquidity: parseFloat(data.liquidity || 0),
                volume_24h: parseFloat(data.volume_24h || 0),
                fee: parseFloat(data.fee || 0),
                slippage: parseFloat(data.estimated_slippage || 0),
                timestamp: new Date(data.timestamp || Date.now()),
                pair_address: data.pair_address,
                confidence: parseFloat(data.confidence || 1)
            };

        } catch (error) {
            console.error(`Error fetching price from ${dexId}:`, error);
            return null;
        }
    }

    /**
     * Find best price across DEXs
     * Method: findBestPrice()
     */
    findBestPrice(tokenAddress, tradeType = 'buy') {
        try {
            const prices = this.priceData.get(tokenAddress);
            if (!prices || prices.size === 0) {
                return null;
            }

            let bestPrice = null;
            let bestDex = null;

            for (const [dexId, priceData] of prices) {
                if (!priceData || !priceData.price) continue;

                const effectivePrice = this.calculateEffectivePrice(
                    priceData.price, 
                    priceData.fee, 
                    priceData.slippage, 
                    tradeType
                );

                if (!bestPrice || 
                    (tradeType === 'buy' && effectivePrice < bestPrice) ||
                    (tradeType === 'sell' && effectivePrice > bestPrice)) {
                    bestPrice = effectivePrice;
                    bestDex = dexId;
                }
            }

            return {
                dex: bestDex,
                price: bestPrice,
                data: prices.get(bestDex)
            };

        } catch (error) {
            console.error('Error finding best price:', error);
            return null;
        }
    }

    /**
     * Calculate arbitrage opportunities
     * Method: calculateArbitrage()
     */
    calculateArbitrage(tokenAddress) {
        try {
            const prices = this.priceData.get(tokenAddress);
            if (!prices || prices.size < 2) {
                return [];
            }

            const opportunities = [];
            const priceArray = Array.from(prices.entries());

            // Compare all DEX pairs
            for (let i = 0; i < priceArray.length; i++) {
                for (let j = i + 1; j < priceArray.length; j++) {
                    const [buyDex, buyData] = priceArray[i];
                    const [sellDex, sellData] = priceArray[j];

                    if (!buyData || !sellData || !buyData.price || !sellData.price) continue;

                    // Calculate effective prices including fees
                    const buyPrice = this.calculateEffectivePrice(
                        buyData.price, buyData.fee, buyData.slippage, 'buy'
                    );
                    const sellPrice = this.calculateEffectivePrice(
                        sellData.price, sellData.fee, sellData.slippage, 'sell'
                    );

                    // Check both directions
                    this.checkArbitrageOpportunity(
                        tokenAddress, buyDex, sellDex, buyPrice, sellPrice, 
                        buyData, sellData, opportunities
                    );
                    
                    this.checkArbitrageOpportunity(
                        tokenAddress, sellDex, buyDex, sellPrice, buyPrice, 
                        sellData, buyData, opportunities
                    );
                }
            }

            // Sort by profit potential
            opportunities.sort((a, b) => b.profitPercentage - a.profitPercentage);

            // Store opportunities
            this.arbitrageOpportunities.set(tokenAddress, opportunities);

            return opportunities;

        } catch (error) {
            console.error('Error calculating arbitrage:', error);
            return [];
        }
    }

    /**
     * Check individual arbitrage opportunity
     */
    checkArbitrageOpportunity(tokenAddress, buyDex, sellDex, buyPrice, sellPrice, 
                             buyData, sellData, opportunities) {
        try {
            if (sellPrice <= buyPrice) return;

            const profit = sellPrice - buyPrice;
            const profitPercentage = (profit / buyPrice) * 100;

            // Minimum profit threshold (0.5%)
            if (profitPercentage < 0.5) return;

            // Calculate maximum trade size based on liquidity
            const maxTradeSize = Math.min(
                buyData.liquidity * 0.1, // 10% of buy side liquidity
                sellData.liquidity * 0.1  // 10% of sell side liquidity
            );

            const opportunity = {
                tokenAddress,
                buyDex,
                sellDex,
                buyPrice,
                sellPrice,
                profit,
                profitPercentage,
                maxTradeSize,
                estimatedGas: this.estimateGasForArbitrage(buyDex, sellDex),
                confidence: Math.min(buyData.confidence, sellData.confidence),
                urgency: this.calculateUrgency(profitPercentage, buyData, sellData),
                timeWindow: this.estimateTimeWindow(buyData, sellData),
                risks: this.assessRisks(buyData, sellData),
                createdAt: new Date()
            };

            opportunities.push(opportunity);

        } catch (error) {
            console.error('Error checking arbitrage opportunity:', error);
        }
    }

    /**
     * Calculate effective price including fees and slippage
     */
    calculateEffectivePrice(price, fee, slippage, tradeType) {
        const feeMultiplier = tradeType === 'buy' ? (1 + fee) : (1 - fee);
        const slippageMultiplier = tradeType === 'buy' ? (1 + slippage) : (1 - slippage);
        
        return price * feeMultiplier * slippageMultiplier;
    }

    /**
     * Analyze prices and generate insights
     */
    analyzePrices(tokenAddress, prices) {
        try {
            const analysis = {
                bestBuy: this.findBestPrice(tokenAddress, 'buy'),
                bestSell: this.findBestPrice(tokenAddress, 'sell'),
                arbitrage: this.calculateArbitrage(tokenAddress),
                priceSpread: null,
                averagePrice: null,
                liquidityTotal: 0,
                volumeTotal: 0
            };

            // Calculate price spread and average
            const priceValues = Array.from(prices.values())
                .filter(data => data && data.price)
                .map(data => data.price);

            if (priceValues.length > 0) {
                const minPrice = Math.min(...priceValues);
                const maxPrice = Math.max(...priceValues);
                analysis.priceSpread = ((maxPrice - minPrice) / minPrice) * 100;
                analysis.averagePrice = priceValues.reduce((sum, price) => sum + price, 0) / priceValues.length;
            }

            // Calculate totals
            for (const data of prices.values()) {
                if (data) {
                    analysis.liquidityTotal += data.liquidity || 0;
                    analysis.volumeTotal += data.volume_24h || 0;
                }
            }

            return analysis;

        } catch (error) {
            console.error('Error analyzing prices:', error);
            return null;
        }
    }

    /**
     * Estimate gas cost for arbitrage
     */
    estimateGasForArbitrage(buyDex, sellDex) {
        // Base gas estimates for different DEX types
        const gasEstimates = {
            uniswap_v2: 150000,
            uniswap_v3: 180000,
            sushiswap: 150000,
            pancakeswap: 120000,
            curve: 200000,
            balancer: 220000
        };

        const buyGas = gasEstimates[buyDex] || 150000;
        const sellGas = gasEstimates[sellDex] || 150000;
        
        return buyGas + sellGas + 50000; // Additional overhead
    }

    /**
     * Calculate opportunity urgency
     */
    calculateUrgency(profitPercentage, buyData, sellData) {
        let urgency = 'low';
        
        if (profitPercentage > 5) urgency = 'critical';
        else if (profitPercentage > 2) urgency = 'high';
        else if (profitPercentage > 1) urgency = 'medium';
        
        // Adjust based on confidence
        const avgConfidence = (buyData.confidence + sellData.confidence) / 2;
        if (avgConfidence < 0.5) urgency = 'low';
        
        return urgency;
    }

    /**
     * Estimate time window for opportunity
     */
    estimateTimeWindow(buyData, sellData) {
        // Higher slippage = shorter window
        const avgSlippage = (buyData.slippage + sellData.slippage) / 2;
        
        if (avgSlippage > 0.02) return '30s';
        if (avgSlippage > 0.01) return '2m';
        if (avgSlippage > 0.005) return '5m';
        return '10m';
    }

    /**
     * Assess arbitrage risks
     */
    assessRisks(buyData, sellData) {
        const risks = [];
        
        if (buyData.slippage > 0.02 || sellData.slippage > 0.02) {
            risks.push('High slippage risk');
        }
        
        if (buyData.liquidity < 10000 || sellData.liquidity < 10000) {
            risks.push('Low liquidity');
        }
        
        if (buyData.confidence < 0.7 || sellData.confidence < 0.7) {
            risks.push('Price uncertainty');
        }
        
        return risks;
    }

    /**
     * Update DEX status
     */
    updateDEXStatus(dexId, status, error = null) {
        const dex = this.dexes.get(dexId);
        if (!dex) return;

        dex.lastUpdate = new Date();
        
        if (status === 'success') {
            dex.errorCount = 0;
            dex.priceCount++;
        } else {
            dex.errorCount++;
            console.warn(`DEX ${dexId} error (${dex.errorCount}):`, error);
        }

        // Disable DEX if too many errors
        if (dex.errorCount >= 3) {
            dex.isActive = false;
            console.warn(`DEX ${dexId} disabled due to errors`);
        }
    }

    /**
     * Update price comparison display
     */
    updatePriceComparisonDisplay(tokenAddress, prices, analysis) {
        try {
            const container = document.getElementById('dex-price-comparison');
            if (!container) return;

            // Create comparison table
            const tableHTML = this.generatePriceTable(prices, analysis);
            container.innerHTML = tableHTML;

            // Update arbitrage alerts
            this.updateArbitrageAlerts(analysis.arbitrage);

            // Update best price indicators
            this.updateBestPriceIndicators(analysis);

        } catch (error) {
            console.error('Error updating price comparison display:', error);
        }
    }

    /**
     * Generate price comparison table
     */
    generatePriceTable(prices, analysis) {
        let tableHTML = `
            <div class="dex-comparison-table">
                <div class="table-header">
                    <h5><i class="bi bi-list-ul"></i> DEX Price Comparison</h5>
                    <div class="price-spread">Spread: ${analysis.priceSpread?.toFixed(2) || '0.00'}%</div>
                </div>
                <div class="table-responsive">
                    <table class="table table-dark table-hover">
                        <thead>
                            <tr>
                                <th>DEX</th>
                                <th>Price</th>
                                <th>Liquidity</th>
                                <th>Volume 24h</th>
                                <th>Fee</th>
                                <th>Est. Slippage</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        for (const [dexId, priceData] of prices) {
            const dexConfig = this.supportedDEXes[dexId];
            const isBestBuy = analysis.bestBuy?.dex === dexId;
            const isBestSell = analysis.bestSell?.dex === dexId;
            
            tableHTML += `
                <tr class="${isBestBuy ? 'best-buy' : ''} ${isBestSell ? 'best-sell' : ''}">
                    <td>
                        <span class="dex-icon">${dexConfig.icon}</span>
                        <span class="dex-name">${dexConfig.name}</span>
                        ${isBestBuy ? '<span class="badge bg-success ms-1">Best Buy</span>' : ''}
                        ${isBestSell ? '<span class="badge bg-primary ms-1">Best Sell</span>' : ''}
                    </td>
                    <td class="price-cell">
                        $${priceData.price.toFixed(6)}
                        <div class="price-confidence">
                            <small>Confidence: ${(priceData.confidence * 100).toFixed(0)}%</small>
                        </div>
                    </td>
                    <td>${this.formatCurrency(priceData.liquidity)}</td>
                    <td>${this.formatCurrency(priceData.volume_24h)}</td>
                    <td>${(priceData.fee * 100).toFixed(2)}%</td>
                    <td class="${priceData.slippage > 0.02 ? 'text-warning' : ''}">
                        ${(priceData.slippage * 100).toFixed(2)}%
                    </td>
                    <td>
                        <span class="status-indicator ${priceData.confidence > 0.8 ? 'status-good' : 'status-warning'}">
                            ${priceData.confidence > 0.8 ? 'Good' : 'Limited'}
                        </span>
                    </td>
                </tr>
            `;
        }

        tableHTML += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        return tableHTML;
    }

    /**
     * Update arbitrage alerts
     */
    updateArbitrageAlerts(opportunities) {
        try {
            const alertContainer = document.getElementById('arbitrage-alerts');
            if (!alertContainer) return;

            if (opportunities.length === 0) {
                alertContainer.innerHTML = '<div class="no-opportunities">No arbitrage opportunities found</div>';
                return;
            }

            let alertsHTML = '<div class="arbitrage-opportunities">';
            
            opportunities.slice(0, 5).forEach(opp => {
                const urgencyClass = this.getUrgencyClass(opp.urgency);
                
                alertsHTML += `
                    <div class="arbitrage-alert ${urgencyClass}" data-opportunity="${JSON.stringify(opp).replace(/"/g, '&quot;')}">
                        <div class="opportunity-header">
                            <span class="profit-badge">${opp.profitPercentage.toFixed(2)}%</span>
                            <span class="route">${this.supportedDEXes[opp.buyDex].icon} → ${this.supportedDEXes[opp.sellDex].icon}</span>
                            <span class="urgency ${opp.urgency}">${opp.urgency.toUpperCase()}</span>
                        </div>
                        <div class="opportunity-details">
                            <div>Buy: ${this.supportedDEXes[opp.buyDex].name} @ $${opp.buyPrice.toFixed(6)}</div>
                            <div>Sell: ${this.supportedDEXes[opp.sellDex].name} @ $${opp.sellPrice.toFixed(6)}</div>
                            <div>Max Size: ${this.formatCurrency(opp.maxTradeSize)}</div>
                            <div>Time Window: ${opp.timeWindow}</div>
                        </div>
                        <button class="btn btn-sm btn-success execute-arbitrage" 
                                data-buy-dex="${opp.buyDex}" 
                                data-sell-dex="${opp.sellDex}">
                            Execute
                        </button>
                    </div>
                `;
            });
            
            alertsHTML += '</div>';
            alertContainer.innerHTML = alertsHTML;

        } catch (error) {
            console.error('Error updating arbitrage alerts:', error);
        }
    }

    /**
     * Update best price indicators
     */
    updateBestPriceIndicators(analysis) {
        try {
            // Update best buy indicator
            const bestBuyElement = document.getElementById('best-buy-dex');
            if (bestBuyElement && analysis.bestBuy) {
                const dexConfig = this.supportedDEXes[analysis.bestBuy.dex];
                bestBuyElement.innerHTML = `
                    <span class="dex-icon">${dexConfig.icon}</span>
                    <span class="dex-name">${dexConfig.name}</span>
                    <span class="price">$${analysis.bestBuy.price.toFixed(6)}</span>
                `;
            }

            // Update best sell indicator
            const bestSellElement = document.getElementById('best-sell-dex');
            if (bestSellElement && analysis.bestSell) {
                const dexConfig = this.supportedDEXes[analysis.bestSell.dex];
                bestSellElement.innerHTML = `
                    <span class="dex-icon">${dexConfig.icon}</span>
                    <span class="dex-name">${dexConfig.name}</span>
                    <span class="price">$${analysis.bestSell.price.toFixed(6)}</span>
                `;
            }

        } catch (error) {
            console.error('Error updating best price indicators:', error);
        }
    }

    /**
     * Get urgency CSS class
     */
    getUrgencyClass(urgency) {
        const classes = {
            'critical': 'alert-danger',
            'high': 'alert-warning',
            'medium': 'alert-info',
            'low': 'alert-secondary'
        };
        return classes[urgency] || 'alert-secondary';
    }

    /**
     * Format currency for display
     */
    formatCurrency(amount) {
        if (amount >= 1e9) {
            return '$' + (amount / 1e9).toFixed(1) + 'B';
        } else if (amount >= 1e6) {
            return '$' + (amount / 1e6).toFixed(1) + 'M';
        } else if (amount >= 1e3) {
            return '$' + (amount / 1e3).toFixed(1) + 'K';
        }
        return '$' + amount.toFixed(2);
    }

    /**
     * Start price aggregation interval
     */
    startPriceAggregation() {
        // Update prices every 30 seconds
        this.updateInterval = setInterval(() => {
            const activeTokens = this.getActiveTokens();
            activeTokens.forEach(tokenAddress => {
                this.aggregatePrices(tokenAddress);
            });
        }, 30000);
    }

    /**
     * Get active tokens for monitoring
     */
    getActiveTokens() {
        // Get tokens from current UI state
        const tokenElements = document.querySelectorAll('[data-token-address]');
        return Array.from(tokenElements).map(el => el.dataset.tokenAddress);
    }

    /**
     * Bind event handlers
     */
    bindEvents() {
        // Execute arbitrage buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.execute-arbitrage')) {
                this.handleArbitrageExecution(e.target);
            }
        });

        // DEX filter toggles
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-dex-filter]')) {
                this.handleDEXFilter(e.target);
            }
        });
    }

    /**
     * Handle arbitrage execution
     */
    async handleArbitrageExecution(button) {
        try {
            const buyDex = button.dataset.buyDex;
            const sellDex = button.dataset.sellDex;
            
            // Show confirmation modal
            const confirmed = await this.showArbitrageConfirmation(buyDex, sellDex);
            if (!confirmed) return;

            // Execute arbitrage (placeholder)
            console.log(`Executing arbitrage: ${buyDex} → ${sellDex}`);
            
            // In real implementation, this would call the trading API
            // await this.executeArbitrageTrade(buyDex, sellDex, opportunity);
            
        } catch (error) {
            console.error('Error executing arbitrage:', error);
        }
    }

    /**
     * Show arbitrage confirmation modal
     */
    async showArbitrageConfirmation(buyDex, sellDex) {
        return new Promise((resolve) => {
            const confirmed = confirm(
                `Execute arbitrage trade?\n\n` +
                `Buy on: ${this.supportedDEXes[buyDex].name}\n` +
                `Sell on: ${this.supportedDEXes[sellDex].name}\n\n` +
                `This action cannot be undone.`
            );
            resolve(confirmed);
        });
    }

    /**
     * Handle DEX filter changes
     */
    handleDEXFilter(checkbox) {
        const dexId = checkbox.dataset.dexFilter;
        const dex = this.dexes.get(dexId);
        
        if (dex) {
            dex.isActive = checkbox.checked;
            console.log(`DEX ${dexId} ${dex.isActive ? 'enabled' : 'disabled'}`);
        }
    }

    /**
     * Clean up resources
     */
    destroy() {
        try {
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
            }

            this.dexes.clear();
            this.priceData.clear();
            this.arbitrageOpportunities.clear();

            console.log('✅ DEXComparison destroyed');
        } catch (error) {
            console.error('Error destroying DEXComparison:', error);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DEXComparison;
} else {
    window.DEXComparison = DEXComparison;
}