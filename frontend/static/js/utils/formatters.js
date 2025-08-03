/**
 * Data Formatting Utility Module
 * File: frontend/static/js/utils/formatters.js
 * 
 * Professional data formatting utilities for DEX Sniper Pro.
 * Handles currency, numbers, dates, addresses, and specialized trading data.
 */

class Formatters {
    constructor() {
        this.locale = 'en-US';
        this.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        
        // Initialize formatters
        this.initializeFormatters();
        
        console.log('🔧 Formatters initialized');
    }

    /**
     * Initialize number and date formatters
     */
    initializeFormatters() {
        try {
            // Currency formatters
            this.currencyFormatter = new Intl.NumberFormat(this.locale, {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 6
            });

            this.cryptoFormatter = new Intl.NumberFormat(this.locale, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 8,
                useGrouping: true
            });

            // Percentage formatter
            this.percentFormatter = new Intl.NumberFormat(this.locale, {
                style: 'percent',
                minimumFractionDigits: 1,
                maximumFractionDigits: 2
            });

            // Date formatters
            this.dateFormatter = new Intl.DateTimeFormat(this.locale, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                timeZone: this.timezone
            });

            this.timeFormatter = new Intl.DateTimeFormat(this.locale, {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZone: this.timezone
            });

            this.dateTimeFormatter = new Intl.DateTimeFormat(this.locale, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                timeZone: this.timezone
            });

        } catch (error) {
            console.error('❌ Failed to initialize formatters:', error);
            // Fallback to basic formatting
            this.useBasicFormatters();
        }
    }

    /**
     * Fallback to basic formatters
     */
    useBasicFormatters() {
        this.currencyFormatter = {
            format: (value) => `$${this.formatNumber(value, 2)}`
        };
        this.percentFormatter = {
            format: (value) => `${(value * 100).toFixed(2)}%`
        };
    }

    // Currency and Price Formatting

    /**
     * Format currency with proper decimals and symbols
     * @param {number} value - The value to format
     * @param {string} currency - Currency code (default: USD)
     * @returns {string} Formatted currency string
     */
    formatCurrency(value, currency = 'USD') {
        if (value === null || value === undefined || isNaN(value)) {
            return '-';
        }

        try {
            if (currency === 'USD') {
                return this.currencyFormatter.format(value);
            }

            // For other currencies, use basic formatting
            return `${this.formatNumber(value, 6)} ${currency}`;

        } catch (error) {
            console.error('❌ Currency formatting error:', error);
            return `$${this.formatNumber(value, 2)}`;
        }
    }

    /**
     * Format crypto prices with dynamic precision
     * @param {number} price - The price to format
     * @param {string} symbol - Token symbol
     * @returns {string} Formatted price string
     */
    formatCryptoPrice(price, symbol = '') {
        if (price === null || price === undefined || isNaN(price)) {
            return '-';
        }

        try {
            let decimals = 2;
            
            // Dynamic decimal places based on price magnitude
            if (price < 0.001) {
                decimals = 8;
            } else if (price < 0.01) {
                decimals = 6;
            } else if (price < 1) {
                decimals = 4;
            } else if (price < 100) {
                decimals = 3;
            }

            const formatted = this.cryptoFormatter.format(price);
            return symbol ? `${formatted} ${symbol}` : formatted;

        } catch (error) {
            console.error('❌ Crypto price formatting error:', error);
            return this.formatNumber(price, 6);
        }
    }

    /**
     * Format large numbers with appropriate suffixes
     * @param {number} value - The value to format
     * @param {number} decimals - Number of decimal places
     * @returns {string} Formatted number with suffix
     */
    formatLargeNumber(value, decimals = 1) {
        if (value === null || value === undefined || isNaN(value)) {
            return '-';
        }

        const suffixes = ['', 'K', 'M', 'B', 'T'];
        let suffixIndex = 0;
        let scaledValue = Math.abs(value);

        while (scaledValue >= 1000 && suffixIndex < suffixes.length - 1) {
            scaledValue /= 1000;
            suffixIndex++;
        }

        const sign = value < 0 ? '-' : '';
        const formatted = this.formatNumber(scaledValue, decimals);
        
        return `${sign}${formatted}${suffixes[suffixIndex]}`;
    }

    /**
     * Format basic numbers with commas and decimals
     * @param {number} value - The value to format
     * @param {number} decimals - Number of decimal places
     * @returns {string} Formatted number string
     */
    formatNumber(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '-';
        }

        try {
            return new Intl.NumberFormat(this.locale, {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals,
                useGrouping: true
            }).format(value);

        } catch (error) {
            console.error('❌ Number formatting error:', error);
            return value.toFixed(decimals);
        }
    }

    // Percentage Formatting

    /**
     * Format percentage with appropriate styling
     * @param {number} value - The percentage value (0.1 = 10%)
     * @param {number} decimals - Number of decimal places
     * @returns {string} Formatted percentage string
     */
    formatPercentage(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '-';
        }

        try {
            const percentage = value * 100;
            return `${this.formatNumber(percentage, decimals)}%`;

        } catch (error) {
            console.error('❌ Percentage formatting error:', error);
            return `${(value * 100).toFixed(decimals)}%`;
        }
    }

    /**
     * Format percentage change with color indication
     * @param {number} value - The percentage change
     * @param {boolean} includeHtml - Whether to include HTML styling
     * @returns {string} Formatted percentage change
     */
    formatPercentageChange(value, includeHtml = true) {
        if (value === null || value === undefined || isNaN(value)) {
            return '-';
        }

        const percentage = this.formatPercentage(value);
        const sign = value > 0 ? '+' : '';
        const formatted = `${sign}${percentage}`;

        if (!includeHtml) {
            return formatted;
        }

        const colorClass = value > 0 ? 'text-success' : 
                          value < 0 ? 'text-danger' : 
                          'text-muted';

        return `<span class="${colorClass}">${formatted}</span>`;
    }

    // Date and Time Formatting

    /**
     * Format date to readable string
     * @param {Date|string|number} date - Date to format
     * @returns {string} Formatted date string
     */
    formatDate(date) {
        if (!date) return '-';

        try {
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
                return 'Invalid Date';
            }

            return this.dateFormatter.format(dateObj);

        } catch (error) {
            console.error('❌ Date formatting error:', error);
            return 'Invalid Date';
        }
    }

    /**
     * Format time to readable string
     * @param {Date|string|number} date - Date to format
     * @returns {string} Formatted time string
     */
    formatTime(date) {
        if (!date) return '-';

        try {
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
                return 'Invalid Time';
            }

            return this.timeFormatter.format(dateObj);

        } catch (error) {
            console.error('❌ Time formatting error:', error);
            return 'Invalid Time';
        }
    }

    /**
     * Format datetime to readable string
     * @param {Date|string|number} date - Date to format
     * @returns {string} Formatted datetime string
     */
    formatDateTime(date) {
        if (!date) return '-';

        try {
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
                return 'Invalid DateTime';
            }

            return this.dateTimeFormatter.format(dateObj);

        } catch (error) {
            console.error('❌ DateTime formatting error:', error);
            return 'Invalid DateTime';
        }
    }

    /**
     * Format relative time (time ago)
     * @param {Date|string|number} date - Date to format
     * @returns {string} Relative time string
     */
    formatTimeAgo(date) {
        if (!date) return '-';

        try {
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
                return 'Invalid Date';
            }

            const now = new Date();
            const diffMs = now - dateObj;
            const diffSecs = Math.floor(diffMs / 1000);
            const diffMins = Math.floor(diffSecs / 60);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffSecs < 60) {
                return diffSecs <= 1 ? 'just now' : `${diffSecs}s ago`;
            } else if (diffMins < 60) {
                return `${diffMins}m ago`;
            } else if (diffHours < 24) {
                return `${diffHours}h ago`;
            } else if (diffDays < 7) {
                return `${diffDays}d ago`;
            } else {
                return this.formatDate(dateObj);
            }

        } catch (error) {
            console.error('❌ TimeAgo formatting error:', error);
            return 'Invalid Date';
        }
    }

    // Blockchain and Crypto Specific Formatting

    /**
     * Format wallet address with truncation
     * @param {string} address - Wallet address
     * @param {number} startChars - Characters to show at start
     * @param {number} endChars - Characters to show at end
     * @returns {string} Formatted address string
     */
    formatAddress(address, startChars = 6, endChars = 4) {
        if (!address || typeof address !== 'string') {
            return '-';
        }

        if (address.length <= startChars + endChars) {
            return address;
        }

        return `${address.slice(0, startChars)}...${address.slice(-endChars)}`;
    }

    /**
     * Format transaction hash
     * @param {string} hash - Transaction hash
     * @returns {string} Formatted hash string
     */
    formatTxHash(hash) {
        return this.formatAddress(hash, 8, 6);
    }

    /**
     * Format risk score with color coding
     * @param {number} score - Risk score (0-100)
     * @param {boolean} includeHtml - Whether to include HTML styling
     * @returns {string} Formatted risk score
     */
    formatRiskScore(score, includeHtml = true) {
        if (score === null || score === undefined || isNaN(score)) {
            return '-';
        }

        const formatted = `${Math.round(score)}/100`;

        if (!includeHtml) {
            return formatted;
        }

        let colorClass = 'text-success';  // Low risk (green)
        if (score > 30) colorClass = 'text-warning';    // Medium risk (yellow)
        if (score > 70) colorClass = 'text-danger';     // High risk (red)

        return `<span class="${colorClass}">${formatted}</span>`;
    }

    /**
     * Format market cap with appropriate suffix
     * @param {number} marketCap - Market capitalization
     * @returns {string} Formatted market cap string
     */
    formatMarketCap(marketCap) {
        if (marketCap === null || marketCap === undefined || isNaN(marketCap)) {
            return '-';
        }

        return `$${this.formatLargeNumber(marketCap, 1)}`;
    }

    /**
     * Format trading volume
     * @param {number} volume - Trading volume
     * @returns {string} Formatted volume string
     */
    formatVolume(volume) {
        if (volume === null || volume === undefined || isNaN(volume)) {
            return '-';
        }

        return `$${this.formatLargeNumber(volume, 1)}`;
    }

    /**
     * Format liquidity amount
     * @param {number} liquidity - Liquidity amount
     * @returns {string} Formatted liquidity string
     */
    formatLiquidity(liquidity) {
        if (liquidity === null || liquidity === undefined || isNaN(liquidity)) {
            return '-';
        }

        return `$${this.formatLargeNumber(liquidity, 1)}`;
    }

    // Utility Methods

    /**
     * Sanitize input for display
     * @param {string} input - Input to sanitize
     * @returns {string} Sanitized string
     */
    sanitizeForDisplay(input) {
        if (typeof input !== 'string') {
            return String(input || '');
        }

        return input
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Format file size
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        if (!bytes || isNaN(bytes)) return '-';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
    }

    /**
     * Format duration in milliseconds
     * @param {number} ms - Duration in milliseconds
     * @returns {string} Formatted duration string
     */
    formatDuration(ms) {
        if (!ms || isNaN(ms)) return '-';

        if (ms < 1000) {
            return `${Math.round(ms)}ms`;
        } else if (ms < 60000) {
            return `${(ms / 1000).toFixed(1)}s`;
        } else if (ms < 3600000) {
            return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
        } else {
            const hours = Math.floor(ms / 3600000);
            const minutes = Math.floor((ms % 3600000) / 60000);
            return `${hours}h ${minutes}m`;
        }
    }

    /**
     * Get status badge HTML
     * @param {string} status - Status value
     * @param {Object} colorMap - Optional color mapping
     * @returns {string} Status badge HTML
     */
    formatStatusBadge(status, colorMap = null) {
        if (!status) return '-';

        const defaultColors = {
            'active': 'success',
            'inactive': 'secondary',
            'pending': 'warning',
            'error': 'danger',
            'success': 'success',
            'failed': 'danger',
            'completed': 'success',
            'processing': 'info'
        };

        const colors = colorMap || defaultColors;
        const color = colors[status.toLowerCase()] || 'secondary';
        const displayText = status.charAt(0).toUpperCase() + status.slice(1);

        return `<span class="badge bg-${color}">${displayText}</span>`;
    }
}

// Create and export global instance
window.Formatters = Formatters;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Formatters;
}

console.log('🎨 Formatters module loaded successfully');