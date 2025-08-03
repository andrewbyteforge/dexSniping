/**
 * Input Validation Utility Module
 * File: frontend/static/js/utils/validators.js
 * 
 * Comprehensive input validation and sanitization for DEX Sniper Pro.
 * Provides security, data integrity, and user input validation.
 */

class Validators {
    constructor() {
        this.patterns = this.initializePatterns();
        this.errorMessages = this.initializeErrorMessages();
        
        console.log('🔒 Validators initialized');
    }

    /**
     * Initialize regex patterns for validation
     * @returns {Object} Validation patterns
     */
    initializePatterns() {
        return {
            // Blockchain addresses
            ETHEREUM_ADDRESS: /^0x[a-fA-F0-9]{40}$/,
            BITCOIN_ADDRESS: /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/,
            SOLANA_ADDRESS: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/,
            
            // Transaction hashes
            TX_HASH: /^0x[a-fA-F0-9]{64}$/,
            
            // Network and protocol identifiers
            CHAIN_ID: /^\d+$/,
            
            // Token symbols and names
            TOKEN_SYMBOL: /^[A-Z0-9]{1,10}$/i,
            TOKEN_NAME: /^[a-zA-Z0-9\s\-\.]{1,50}$/,
            
            // Amounts and prices
            DECIMAL_NUMBER: /^[0-9]*\.?[0-9]+$/,
            POSITIVE_NUMBER: /^[0-9]*\.?[0-9]*[1-9]+[0-9]*$/,
            INTEGER: /^[0-9]+$/,
            
            // User input
            EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            USERNAME: /^[a-zA-Z0-9_]{3,20}$/,
            PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
            
            // URLs and endpoints
            URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
            WS_URL: /^wss?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
            
            // Search and filter
            SEARCH_QUERY: /^[a-zA-Z0-9\s\-\.@#$%&*()_+=[\]{}|\\:";'<>?,\/]{0,100}$/,
            
            // Hex colors and values
            HEX_COLOR: /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/,
            HEX_VALUE: /^0x[a-fA-F0-9]+$/
        };
    }

    /**
     * Initialize error messages
     * @returns {Object} Error message templates
     */
    initializeErrorMessages() {
        return {
            REQUIRED: 'This field is required',
            INVALID_FORMAT: 'Invalid format',
            INVALID_ADDRESS: 'Invalid blockchain address',
            INVALID_TX_HASH: 'Invalid transaction hash',
            INVALID_AMOUNT: 'Invalid amount',
            AMOUNT_TOO_SMALL: 'Amount too small',
            AMOUNT_TOO_LARGE: 'Amount too large',
            INVALID_EMAIL: 'Invalid email address',
            INVALID_USERNAME: 'Username must be 3-20 characters, alphanumeric and underscore only',
            WEAK_PASSWORD: 'Password must be at least 8 characters with uppercase, lowercase, and number',
            INVALID_URL: 'Invalid URL format',
            INVALID_TOKEN_SYMBOL: 'Token symbol must be 1-10 alphanumeric characters',
            INVALID_SEARCH: 'Search query contains invalid characters',
            OUT_OF_RANGE: 'Value out of valid range',
            STRING_TOO_LONG: 'Text is too long',
            STRING_TOO_SHORT: 'Text is too short'
        };
    }

    // Basic Validation Methods

    /**
     * Check if value is not null, undefined, or empty
     * @param {any} value - Value to check
     * @returns {boolean} True if value exists
     */
    isRequired(value) {
        if (value === null || value === undefined) {
            return false;
        }
        
        if (typeof value === 'string') {
            return value.trim().length > 0;
        }
        
        if (Array.isArray(value)) {
            return value.length > 0;
        }
        
        return true;
    }

    /**
     * Validate string length
     * @param {string} value - String to validate
     * @param {number} min - Minimum length
     * @param {number} max - Maximum length
     * @returns {Object} Validation result
     */
    validateStringLength(value, min = 0, max = Infinity) {
        if (!this.isRequired(value)) {
            return { isValid: false, error: this.errorMessages.REQUIRED };
        }

        const length = value.trim().length;
        
        if (length < min) {
            return { 
                isValid: false, 
                error: `${this.errorMessages.STRING_TOO_SHORT} (minimum: ${min})` 
            };
        }
        
        if (length > max) {
            return { 
                isValid: false, 
                error: `${this.errorMessages.STRING_TOO_LONG} (maximum: ${max})` 
            };
        }

        return { isValid: true };
    }

    /**
     * Validate using regex pattern
     * @param {string} value - Value to validate
     * @param {RegExp} pattern - Regex pattern
     * @param {string} errorMessage - Custom error message
     * @returns {Object} Validation result
     */
    validatePattern(value, pattern, errorMessage = null) {
        if (!this.isRequired(value)) {
            return { isValid: false, error: this.errorMessages.REQUIRED };
        }

        const isValid = pattern.test(value.trim());
        
        return {
            isValid,
            error: isValid ? null : (errorMessage || this.errorMessages.INVALID_FORMAT)
        };
    }

    // Blockchain-Specific Validators

    /**
     * Validate Ethereum address
     * @param {string} address - Address to validate
     * @returns {Object} Validation result
     */
    validateEthereumAddress(address) {
        const result = this.validatePattern(
            address,
            this.patterns.ETHEREUM_ADDRESS,
            this.errorMessages.INVALID_ADDRESS
        );

        if (result.isValid) {
            // Additional checksum validation could be added here
            const trimmed = address.trim();
            if (trimmed !== trimmed.toLowerCase() && trimmed !== trimmed.toUpperCase()) {
                // Mixed case - should validate checksum
                console.warn('Address has mixed case - checksum validation recommended');
            }
        }

        return result;
    }

    /**
     * Validate any blockchain address
     * @param {string} address - Address to validate
     * @param {string} network - Network type (ethereum, bitcoin, solana)
     * @returns {Object} Validation result
     */
    validateAddress(address, network = 'ethereum') {
        switch (network.toLowerCase()) {
            case 'ethereum':
            case 'polygon':
            case 'bsc':
            case 'arbitrum':
            case 'optimism':
            case 'avalanche':
            case 'fantom':
                return this.validateEthereumAddress(address);
            
            case 'bitcoin':
                return this.validatePattern(
                    address,
                    this.patterns.BITCOIN_ADDRESS,
                    this.errorMessages.INVALID_ADDRESS
                );
            
            case 'solana':
                return this.validatePattern(
                    address,
                    this.patterns.SOLANA_ADDRESS,
                    this.errorMessages.INVALID_ADDRESS
                );
            
            default:
                // Default to Ethereum format for EVM chains
                return this.validateEthereumAddress(address);
        }
    }

    /**
     * Validate transaction hash
     * @param {string} hash - Transaction hash to validate
     * @returns {Object} Validation result
     */
    validateTransactionHash(hash) {
        return this.validatePattern(
            hash,
            this.patterns.TX_HASH,
            this.errorMessages.INVALID_TX_HASH
        );
    }

    /**
     * Validate chain ID
     * @param {string|number} chainId - Chain ID to validate
     * @returns {Object} Validation result
     */
    validateChainId(chainId) {
        const strValue = String(chainId).trim();
        
        if (!this.patterns.CHAIN_ID.test(strValue)) {
            return { isValid: false, error: 'Invalid chain ID format' };
        }

        const numValue = parseInt(strValue, 10);
        if (numValue < 1 || numValue > 999999) {
            return { isValid: false, error: 'Chain ID out of valid range' };
        }

        return { isValid: true };
    }

    // Token and Trading Validators

    /**
     * Validate token symbol
     * @param {string} symbol - Token symbol to validate
     * @returns {Object} Validation result
     */
    validateTokenSymbol(symbol) {
        return this.validatePattern(
            symbol,
            this.patterns.TOKEN_SYMBOL,
            this.errorMessages.INVALID_TOKEN_SYMBOL
        );
    }

    /**
     * Validate token name
     * @param {string} name - Token name to validate
     * @returns {Object} Validation result
     */
    validateTokenName(name) {
        const lengthResult = this.validateStringLength(name, 1, 50);
        if (!lengthResult.isValid) {
            return lengthResult;
        }

        return this.validatePattern(
            name,
            this.patterns.TOKEN_NAME,
            'Token name contains invalid characters'
        );
    }

    /**
     * Validate trading amount
     * @param {string|number} amount - Amount to validate
     * @param {number} min - Minimum amount
     * @param {number} max - Maximum amount
     * @returns {Object} Validation result
     */
    validateAmount(amount, min = 0.000001, max = 1000000) {
        if (!this.isRequired(amount)) {
            return { isValid: false, error: this.errorMessages.REQUIRED };
        }

        const strValue = String(amount).trim();
        
        // Check format
        if (!this.patterns.DECIMAL_NUMBER.test(strValue)) {
            return { isValid: false, error: this.errorMessages.INVALID_AMOUNT };
        }

        const numValue = parseFloat(strValue);
        
        // Check if it's a valid number
        if (isNaN(numValue) || !isFinite(numValue)) {
            return { isValid: false, error: this.errorMessages.INVALID_AMOUNT };
        }

        // Check range
        if (numValue < min) {
            return { 
                isValid: false, 
                error: `${this.errorMessages.AMOUNT_TOO_SMALL} (minimum: ${min})` 
            };
        }

        if (numValue > max) {
            return { 
                isValid: false, 
                error: `${this.errorMessages.AMOUNT_TOO_LARGE} (maximum: ${max})` 
            };
        }

        return { isValid: true, value: numValue };
    }

    /**
     * Validate positive number
     * @param {string|number} value - Value to validate
     * @returns {Object} Validation result
     */
    validatePositiveNumber(value) {
        const strValue = String(value).trim();
        
        if (!this.patterns.POSITIVE_NUMBER.test(strValue)) {
            return { isValid: false, error: 'Must be a positive number' };
        }

        const numValue = parseFloat(strValue);
        
        if (numValue <= 0) {
            return { isValid: false, error: 'Must be greater than zero' };
        }

        return { isValid: true, value: numValue };
    }

    /**
     * Validate percentage (0-100)
     * @param {string|number} percentage - Percentage to validate
     * @returns {Object} Validation result
     */
    validatePercentage(percentage) {
        const amountResult = this.validateAmount(percentage, 0, 100);
        
        if (!amountResult.isValid) {
            return {
                isValid: false,
                error: amountResult.error.replace('amount', 'percentage')
            };
        }

        return amountResult;
    }

    // User Input Validators

    /**
     * Validate email address
     * @param {string} email - Email to validate
     * @returns {Object} Validation result
     */
    validateEmail(email) {
        const lengthResult = this.validateStringLength(email, 5, 100);
        if (!lengthResult.isValid) {
            return lengthResult;
        }

        return this.validatePattern(
            email,
            this.patterns.EMAIL,
            this.errorMessages.INVALID_EMAIL
        );
    }

    /**
     * Validate username
     * @param {string} username - Username to validate
     * @returns {Object} Validation result
     */
    validateUsername(username) {
        return this.validatePattern(
            username,
            this.patterns.USERNAME,
            this.errorMessages.INVALID_USERNAME
        );
    }

    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @returns {Object} Validation result with strength info
     */
    validatePassword(password) {
        if (!this.isRequired(password)) {
            return { isValid: false, error: this.errorMessages.REQUIRED };
        }

        const lengthValid = password.length >= 8;
        const hasLower = /[a-z]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[@$!%*?&]/.test(password);

        const strength = {
            length: lengthValid,
            lowercase: hasLower,
            uppercase: hasUpper,
            digit: hasDigit,
            special: hasSpecial
        };

        const isValid = lengthValid && hasLower && hasUpper && hasDigit;
        
        if (!isValid) {
            return { 
                isValid: false, 
                error: this.errorMessages.WEAK_PASSWORD,
                strength 
            };
        }

        // Calculate strength score
        const score = Object.values(strength).filter(Boolean).length;
        const strengthLevel = score <= 3 ? 'weak' : 
                            score === 4 ? 'medium' : 'strong';

        return { 
            isValid: true, 
            strength,
            strengthLevel,
            score 
        };
    }

    /**
     * Validate URL
     * @param {string} url - URL to validate
     * @returns {Object} Validation result
     */
    validateUrl(url) {
        return this.validatePattern(
            url,
            this.patterns.URL,
            this.errorMessages.INVALID_URL
        );
    }

    /**
     * Validate WebSocket URL
     * @param {string} url - WebSocket URL to validate
     * @returns {Object} Validation result
     */
    validateWebSocketUrl(url) {
        return this.validatePattern(
            url,
            this.patterns.WS_URL,
            'Invalid WebSocket URL format'
        );
    }

    // Search and Filter Validators

    /**
     * Validate search query
     * @param {string} query - Search query to validate
     * @returns {Object} Validation result
     */
    validateSearchQuery(query) {
        if (!query || query.trim().length === 0) {
            return { isValid: true, value: '' }; // Empty search is valid
        }

        const lengthResult = this.validateStringLength(query, 1, 100);
        if (!lengthResult.isValid) {
            return lengthResult;
        }

        const patternResult = this.validatePattern(
            query,
            this.patterns.SEARCH_QUERY,
            this.errorMessages.INVALID_SEARCH
        );

        if (patternResult.isValid) {
            return { isValid: true, value: query.trim() };
        }

        return patternResult;
    }

    // Utility Methods

    /**
     * Sanitize string input to prevent XSS
     * @param {string} input - Input to sanitize
     * @returns {string} Sanitized string
     */
    sanitizeInput(input) {
        if (typeof input !== 'string') {
            return String(input || '');
        }

        return input
            .replace(/[<>]/g, '') // Remove HTML tags
            .replace(/javascript:/gi, '') // Remove javascript: protocol
            .replace(/on\w+=/gi, '') // Remove event handlers
            .trim();
    }

    /**
     * Validate multiple fields at once
     * @param {Object} fields - Object with field names as keys and values to validate
     * @param {Object} rules - Validation rules for each field
     * @returns {Object} Validation results
     */
    validateForm(fields, rules) {
        const errors = {};
        const values = {};
        let isValid = true;

        for (const [fieldName, value] of Object.entries(fields)) {
            const fieldRules = rules[fieldName];
            if (!fieldRules) continue;

            let fieldResult = { isValid: true };

            // Apply validation rules in order
            for (const rule of fieldRules) {
                const { validator, ...options } = rule;
                
                if (typeof this[validator] === 'function') {
                    fieldResult = this[validator](value, ...Object.values(options));
                } else {
                    console.warn(`Unknown validator: ${validator}`);
                    continue;
                }

                // If validation fails, break and record error
                if (!fieldResult.isValid) {
                    break;
                }
            }

            if (!fieldResult.isValid) {
                errors[fieldName] = fieldResult.error;
                isValid = false;
            } else {
                values[fieldName] = fieldResult.value !== undefined ? fieldResult.value : value;
            }
        }

        return {
            isValid,
            errors,
            values
        };
    }

    /**
     * Create validation rule
     * @param {string} validator - Validator method name
     * @param {Object} options - Validator options
     * @returns {Object} Validation rule
     */
    createRule(validator, options = {}) {
        return { validator, ...options };
    }

    /**
     * Get error message for field
     * @param {string} field - Field name
     * @param {Object} errors - Errors object
     * @returns {string|null} Error message
     */
    getFieldError(field, errors) {
        return errors[field] || null;
    }

    /**
     * Check if form has any errors
     * @param {Object} errors - Errors object
     * @returns {boolean} True if has errors
     */
    hasErrors(errors) {
        return Object.keys(errors).length > 0;
    }
}

// Create and export global instance
window.Validators = Validators;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Validators;
}

console.log('🔒 Validators module loaded successfully');