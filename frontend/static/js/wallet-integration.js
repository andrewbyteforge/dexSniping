/**
 * Enhanced Wallet Integration - Phase 4D
 * File: frontend/static/js/wallet-integration.js
 * Class: WalletIntegrationManager
 * Methods: connectMetaMask, connectWalletConnect, switchNetwork, signTransaction
 * 
 * Comprehensive wallet integration supporting MetaMask, WalletConnect, and other
 * popular wallets with real trading functionality and secure transaction signing.
 */

class WalletIntegrationManager {
    constructor() {
        this.connectedWallet = null;
        this.connectedAccount = null;
        this.connectedNetwork = null;
        this.walletProvider = null;
        this.walletConnectProvider = null;
        
        // Supported networks configuration
        this.supportedNetworks = {
            ethereum: {
                chainId: '0x1',
                chainName: 'Ethereum Mainnet',
                nativeCurrency: { name: 'Ethereum', symbol: 'ETH', decimals: 18 },
                rpcUrls: ['https://ethereum.publicnode.com'],
                blockExplorerUrls: ['https://etherscan.io']
            },
            polygon: {
                chainId: '0x89',
                chainName: 'Polygon Mainnet',
                nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
                rpcUrls: ['https://polygon-rpc.com'],
                blockExplorerUrls: ['https://polygonscan.com']
            },
            bsc: {
                chainId: '0x38',
                chainName: 'Binance Smart Chain',
                nativeCurrency: { name: 'BNB', symbol: 'BNB', decimals: 18 },
                rpcUrls: ['https://bsc-dataseed.binance.org'],
                blockExplorerUrls: ['https://bscscan.com']
            },
            arbitrum: {
                chainId: '0xa4b1',
                chainName: 'Arbitrum One',
                nativeCurrency: { name: 'Ethereum', symbol: 'ETH', decimals: 18 },
                rpcUrls: ['https://arb1.arbitrum.io/rpc'],
                blockExplorerUrls: ['https://arbiscan.io']
            }
        };
        
        // Wallet types
        this.walletTypes = {
            METAMASK: 'metamask',
            WALLET_CONNECT: 'wallet_connect',
            COINBASE_WALLET: 'coinbase_wallet',
            TRUST_WALLET: 'trust_wallet'
        };
        
        // Connection status
        this.connectionStatus = {
            DISCONNECTED: 'disconnected',
            CONNECTING: 'connecting',
            CONNECTED: 'connected',
            ERROR: 'error'
        };
        
        this.currentStatus = this.connectionStatus.DISCONNECTED;
        this.connectionCallbacks = [];
        this.balanceCache = new Map();
        this.isInitialized = false;
        
        console.log('💼 Wallet Integration Manager initialized');
    }
    
    /**
     * Initialize the wallet integration manager
     */
    async init() {
        try {
            if (this.isInitialized) {
                console.warn('⚠️ Wallet manager already initialized');
                return;
            }
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize WalletConnect if available
            await this.initializeWalletConnect();
            
            // Check for existing connections
            await this.checkExistingConnections();
            
            this.isInitialized = true;
            console.log('✅ Wallet Integration Manager initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize wallet manager:', error);
            throw error;
        }
    }
    
    /**
     * Connect MetaMask wallet
     */
    async connectMetaMask() {
        try {
            console.log('🦊 Connecting to MetaMask...');
            this.setConnectionStatus(this.connectionStatus.CONNECTING);
            
            // Check if MetaMask is installed
            if (!window.ethereum || !window.ethereum.isMetaMask) {
                throw new Error('MetaMask is not installed. Please install MetaMask to continue.');
            }
            
            // Request account access
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });
            
            if (!accounts || accounts.length === 0) {
                throw new Error('No accounts returned from MetaMask');
            }
            
            // Get current network
            const chainId = await window.ethereum.request({
                method: 'eth_chainId'
            });
            
            // Store connection details
            this.connectedWallet = this.walletTypes.METAMASK;
            this.connectedAccount = accounts[0];
            this.connectedNetwork = this.getNetworkFromChainId(chainId);
            this.walletProvider = window.ethereum;
            
            // Setup MetaMask event listeners
            this.setupMetaMaskEventListeners();
            
            // Register connection with backend
            const connectionResult = await this.registerWalletConnection();
            
            this.setConnectionStatus(this.connectionStatus.CONNECTED);
            
            console.log('✅ MetaMask connected successfully:', {
                account: this.connectedAccount,
                network: this.connectedNetwork,
                connectionId: connectionResult.connection_id
            });
            
            // Update UI
            this.updateWalletUI();
            
            // Fetch balances
            await this.fetchBalances();
            
            return {
                success: true,
                wallet: this.walletTypes.METAMASK,
                account: this.connectedAccount,
                network: this.connectedNetwork,
                connectionId: connectionResult.connection_id
            };
            
        } catch (error) {
            console.error('❌ MetaMask connection failed:', error);
            this.setConnectionStatus(this.connectionStatus.ERROR);
            throw new Error(`MetaMask connection failed: ${error.message}`);
        }
    }
    
    /**
     * Connect WalletConnect
     */
    async connectWalletConnect() {
        try {
            console.log('🔗 Connecting to WalletConnect...');
            this.setConnectionStatus(this.connectionStatus.CONNECTING);
            
            // Check if WalletConnect is available
            if (!window.WalletConnect) {
                throw new Error('WalletConnect is not available. Please ensure the library is loaded.');
            }
            
            // Create WalletConnect provider
            const WalletConnectProvider = window.WalletConnectProvider.default;
            
            this.walletConnectProvider = new WalletConnectProvider({
                rpc: {
                    1: this.supportedNetworks.ethereum.rpcUrls[0],
                    137: this.supportedNetworks.polygon.rpcUrls[0],
                    56: this.supportedNetworks.bsc.rpcUrls[0],
                    42161: this.supportedNetworks.arbitrum.rpcUrls[0]
                },
                bridge: 'https://bridge.walletconnect.org',
                qrcodeModal: window.WalletConnectQRCodeModal.default
            });
            
            // Setup WalletConnect event listeners
            this.setupWalletConnectEventListeners();
            
            // Enable connection
            const accounts = await this.walletConnectProvider.enable();
            
            if (!accounts || accounts.length === 0) {
                throw new Error('No accounts returned from WalletConnect');
            }
            
            // Get current network
            const chainId = this.walletConnectProvider.chainId;
            
            // Store connection details
            this.connectedWallet = this.walletTypes.WALLET_CONNECT;
            this.connectedAccount = accounts[0];
            this.connectedNetwork = this.getNetworkFromChainId(`0x${chainId.toString(16)}`);
            this.walletProvider = this.walletConnectProvider;
            
            // Register connection with backend
            const connectionResult = await this.registerWalletConnection();
            
            this.setConnectionStatus(this.connectionStatus.CONNECTED);
            
            console.log('✅ WalletConnect connected successfully:', {
                account: this.connectedAccount,
                network: this.connectedNetwork,
                connectionId: connectionResult.connection_id
            });
            
            // Update UI
            this.updateWalletUI();
            
            // Fetch balances
            await this.fetchBalances();
            
            return {
                success: true,
                wallet: this.walletTypes.WALLET_CONNECT,
                account: this.connectedAccount,
                network: this.connectedNetwork,
                connectionId: connectionResult.connection_id
            };
            
        } catch (error) {
            console.error('❌ WalletConnect connection failed:', error);
            this.setConnectionStatus(this.connectionStatus.ERROR);
            throw new Error(`WalletConnect connection failed: ${error.message}`);
        }
    }
    
    /**
     * Disconnect wallet
     */
    async disconnect() {
        try {
            console.log('🔌 Disconnecting wallet...');
            
            // Disconnect based on wallet type
            if (this.connectedWallet === this.walletTypes.WALLET_CONNECT && this.walletConnectProvider) {
                await this.walletConnectProvider.disconnect();
            }
            
            // Clear connection data
            this.connectedWallet = null;
            this.connectedAccount = null;
            this.connectedNetwork = null;
            this.walletProvider = null;
            this.balanceCache.clear();
            
            this.setConnectionStatus(this.connectionStatus.DISCONNECTED);
            
            // Update UI
            this.updateWalletUI();
            
            console.log('✅ Wallet disconnected successfully');
            
        } catch (error) {
            console.error('❌ Error disconnecting wallet:', error);
        }
    }
    
    /**
     * Switch to a different network
     */
    async switchNetwork(networkName) {
        try {
            console.log(`🔄 Switching to ${networkName} network...`);
            
            const networkConfig = this.supportedNetworks[networkName];
            if (!networkConfig) {
                throw new Error(`Network ${networkName} is not supported`);
            }
            
            if (!this.walletProvider) {
                throw new Error('No wallet connected');
            }
            
            try {
                // Try to switch to the network
                await this.walletProvider.request({
                    method: 'wallet_switchEthereumChain',
                    params: [{ chainId: networkConfig.chainId }]
                });
                
            } catch (switchError) {
                // If network doesn't exist, add it
                if (switchError.code === 4902) {
                    await this.walletProvider.request({
                        method: 'wallet_addEthereumChain',
                        params: [networkConfig]
                    });
                } else {
                    throw switchError;
                }
            }
            
            // Update current network
            this.connectedNetwork = networkName;
            
            // Update UI
            this.updateWalletUI();
            
            // Refresh balances
            await this.fetchBalances();
            
            console.log(`✅ Switched to ${networkName} successfully`);
            
            return true;
            
        } catch (error) {
            console.error(`❌ Failed to switch to ${networkName}:`, error);
            throw new Error(`Network switch failed: ${error.message}`);
        }
    }
    
    /**
     * Sign and send transaction
     */
    async signTransaction(transactionData) {
        try {
            console.log('✍️ Signing transaction...', transactionData);
            
            if (!this.walletProvider) {
                throw new Error('No wallet connected');
            }
            
            if (!this.connectedAccount) {
                throw new Error('No account connected');
            }
            
            // Prepare transaction
            const tx = {
                from: this.connectedAccount,
                to: transactionData.to,
                value: transactionData.value || '0x0',
                data: transactionData.data || '0x',
                gas: transactionData.gas,
                gasPrice: transactionData.gasPrice
            };
            
            // Send transaction
            const txHash = await this.walletProvider.request({
                method: 'eth_sendTransaction',
                params: [tx]
            });
            
            console.log('✅ Transaction signed and sent:', txHash);
            
            return {
                success: true,
                transactionHash: txHash,
                transaction: tx
            };
            
        } catch (error) {
            console.error('❌ Transaction signing failed:', error);
            throw new Error(`Transaction failed: ${error.message}`);
        }
    }
    
    /**
     * Get account balance
     */
    async getBalance(tokenAddress = null) {
        try {
            if (!this.walletProvider || !this.connectedAccount) {
                throw new Error('Wallet not connected');
            }
            
            let balance;
            
            if (!tokenAddress) {
                // Get native token balance
                balance = await this.walletProvider.request({
                    method: 'eth_getBalance',
                    params: [this.connectedAccount, 'latest']
                });
                
                // Convert from wei to ether
                balance = parseFloat(balance) / Math.pow(10, 18);
                
            } else {
                // Get ERC-20 token balance
                balance = await this.getTokenBalance(tokenAddress);
            }
            
            return balance;
            
        } catch (error) {
            console.error('❌ Error getting balance:', error);
            return 0;
        }
    }
    
    /**
     * Get ERC-20 token balance
     */
    async getTokenBalance(tokenAddress) {
        try {
            // ERC-20 balanceOf function signature
            const balanceOfABI = '0x70a08231';
            const paddedAddress = this.connectedAccount.slice(2).padStart(64, '0');
            const data = balanceOfABI + paddedAddress;
            
            const result = await this.walletProvider.request({
                method: 'eth_call',
                params: [{
                    to: tokenAddress,
                    data: data
                }, 'latest']
            });
            
            // Convert hex result to decimal
            const balance = parseInt(result, 16);
            
            // Get token decimals (assume 18 if call fails)
            let decimals = 18;
            try {
                const decimalsABI = '0x313ce567';
                const decimalsResult = await this.walletProvider.request({
                    method: 'eth_call',
                    params: [{
                        to: tokenAddress,
                        data: decimalsABI
                    }, 'latest']
                });
                decimals = parseInt(decimalsResult, 16);
            } catch (e) {
                console.warn('Could not get token decimals, using 18');
            }
            
            return balance / Math.pow(10, decimals);
            
        } catch (error) {
            console.error('❌ Error getting token balance:', error);
            return 0;
        }
    }
    
    /**
     * Fetch and cache balances for connected account
     */
    async fetchBalances() {
        try {
            if (!this.connectedAccount || !this.connectedNetwork) {
                return;
            }
            
            console.log('💰 Fetching wallet balances...');
            
            // Get native token balance
            const nativeBalance = await this.getBalance();
            
            // Cache balance
            const cacheKey = `${this.connectedAccount}_${this.connectedNetwork}_native`;
            this.balanceCache.set(cacheKey, {
                balance: nativeBalance,
                symbol: this.supportedNetworks[this.connectedNetwork].nativeCurrency.symbol,
                timestamp: Date.now()
            });
            
            console.log(`💰 Balance: ${nativeBalance} ${this.supportedNetworks[this.connectedNetwork].nativeCurrency.symbol}`);
            
            // Update UI
            this.updateBalanceUI(nativeBalance);
            
        } catch (error) {
            console.error('❌ Error fetching balances:', error);
        }
    }
    
    /**
     * Register wallet connection with backend
     */
    async registerWalletConnection() {
        try {
            const response = await fetch('/api/v1/wallet/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wallet_type: this.connectedWallet,
                    wallet_address: this.connectedAccount,
                    requested_networks: [this.connectedNetwork]
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Backend registration failed');
            }
            
            const result = await response.json();
            console.log('✅ Wallet registered with backend:', result.connection_id);
            
            return result;
            
        } catch (error) {
            console.error('❌ Backend registration failed:', error);
            // Don't throw - connection can work without backend registration
            return { connection_id: 'offline_' + Date.now() };
        }
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for account changes
        if (window.ethereum) {
            window.ethereum.on('accountsChanged', (accounts) => {
                this.handleAccountsChanged(accounts);
            });
            
            window.ethereum.on('chainChanged', (chainId) => {
                this.handleChainChanged(chainId);
            });
            
            window.ethereum.on('disconnect', () => {
                this.handleDisconnect();
            });
        }
    }
    
    /**
     * Setup MetaMask-specific event listeners
     */
    setupMetaMaskEventListeners() {
        if (!window.ethereum) return;
        
        // Remove existing listeners to prevent duplicates
        window.ethereum.removeAllListeners('accountsChanged');
        window.ethereum.removeAllListeners('chainChanged');
        
        window.ethereum.on('accountsChanged', (accounts) => {
            console.log('🦊 MetaMask accounts changed:', accounts);
            this.handleAccountsChanged(accounts);
        });
        
        window.ethereum.on('chainChanged', (chainId) => {
            console.log('🦊 MetaMask chain changed:', chainId);
            this.handleChainChanged(chainId);
        });
    }
    
    /**
     * Setup WalletConnect-specific event listeners
     */
    setupWalletConnectEventListeners() {
        if (!this.walletConnectProvider) return;
        
        this.walletConnectProvider.on('accountsChanged', (accounts) => {
            console.log('🔗 WalletConnect accounts changed:', accounts);
            this.handleAccountsChanged(accounts);
        });
        
        this.walletConnectProvider.on('chainChanged', (chainId) => {
            console.log('🔗 WalletConnect chain changed:', chainId);
            this.handleChainChanged(`0x${chainId.toString(16)}`);
        });
        
        this.walletConnectProvider.on('disconnect', (code, reason) => {
            console.log('🔗 WalletConnect disconnected:', code, reason);
            this.handleDisconnect();
        });
    }
    
    /**
     * Handle account changes
     */
    async handleAccountsChanged(accounts) {
        if (accounts.length === 0) {
            // No accounts connected
            await this.disconnect();
        } else if (accounts[0] !== this.connectedAccount) {
            // Account changed
            this.connectedAccount = accounts[0];
            this.balanceCache.clear();
            
            // Update UI
            this.updateWalletUI();
            
            // Fetch new balances
            await this.fetchBalances();
            
            // Notify callbacks
            this.notifyConnectionCallbacks('account_changed');
        }
    }
    
    /**
     * Handle chain changes
     */
    async handleChainChanged(chainId) {
        const newNetwork = this.getNetworkFromChainId(chainId);
        
        if (newNetwork !== this.connectedNetwork) {
            this.connectedNetwork = newNetwork;
            this.balanceCache.clear();
            
            // Update UI
            this.updateWalletUI();
            
            // Fetch new balances
            await this.fetchBalances();
            
            // Notify callbacks
            this.notifyConnectionCallbacks('network_changed');
        }
    }
    
    /**
     * Handle disconnect
     */
    async handleDisconnect() {
        await this.disconnect();
        this.notifyConnectionCallbacks('disconnected');
    }
    
    /**
     * Get network name from chain ID
     */
    getNetworkFromChainId(chainId) {
        const networks = {
            '0x1': 'ethereum',
            '0x89': 'polygon',
            '0x38': 'bsc',
            '0xa4b1': 'arbitrum'
        };
        
        return networks[chainId] || 'unknown';
    }
    
    /**
     * Initialize WalletConnect
     */
    async initializeWalletConnect() {
        try {
            // Load WalletConnect libraries if not already loaded
            if (!window.WalletConnect) {
                console.log('📦 Loading WalletConnect libraries...');
                
                // This would load the WalletConnect libraries dynamically
                // For now, assume they're included in the page
                console.log('⚠️ WalletConnect libraries should be included in the page');
            }
        } catch (error) {
            console.warn('⚠️ WalletConnect initialization failed:', error);
        }
    }
    
    /**
     * Check for existing connections
     */
    async checkExistingConnections() {
        try {
            // Check MetaMask
            if (window.ethereum && window.ethereum.isMetaMask) {
                const accounts = await window.ethereum.request({
                    method: 'eth_accounts'
                });
                
                if (accounts && accounts.length > 0) {
                    console.log('🔄 Found existing MetaMask connection');
                    await this.connectMetaMask();
                }
            }
            
            // Check WalletConnect
            if (this.walletConnectProvider && this.walletConnectProvider.connected) {
                console.log('🔄 Found existing WalletConnect connection');
                // Restore WalletConnect connection
                this.connectedWallet = this.walletTypes.WALLET_CONNECT;
                this.connectedAccount = this.walletConnectProvider.accounts[0];
                this.connectedNetwork = this.getNetworkFromChainId(`0x${this.walletConnectProvider.chainId.toString(16)}`);
                this.setConnectionStatus(this.connectionStatus.CONNECTED);
                this.updateWalletUI();
                await this.fetchBalances();
            }
            
        } catch (error) {
            console.warn('⚠️ Error checking existing connections:', error);
        }
    }
    
    /**
     * Set connection status and notify callbacks
     */
    setConnectionStatus(status) {
        this.currentStatus = status;
        this.notifyConnectionCallbacks(status);
    }
    
    /**
     * Add connection status callback
     */
    onConnectionChange(callback) {
        this.connectionCallbacks.push(callback);
    }
    
    /**
     * Notify connection callbacks
     */
    notifyConnectionCallbacks(event) {
        this.connectionCallbacks.forEach(callback => {
            try {
                callback({
                    event,
                    status: this.currentStatus,
                    wallet: this.connectedWallet,
                    account: this.connectedAccount,
                    network: this.connectedNetwork
                });
            } catch (error) {
                console.error('❌ Error in connection callback:', error);
            }
        });
    }
    
    /**
     * Update wallet UI elements
     */
    updateWalletUI() {
        try {
            // Update connection status
            const statusElement = document.getElementById('wallet-status');
            if (statusElement) {
                statusElement.textContent = this.currentStatus;
                statusElement.className = `wallet-status ${this.currentStatus}`;
            }
            
            // Update account display
            const accountElement = document.getElementById('wallet-account');
            if (accountElement) {
                if (this.connectedAccount) {
                    accountElement.textContent = `${this.connectedAccount.slice(0, 6)}...${this.connectedAccount.slice(-4)}`;
                } else {
                    accountElement.textContent = 'Not connected';
                }
            }
            
            // Update network display
            const networkElement = document.getElementById('wallet-network');
            if (networkElement) {
                networkElement.textContent = this.connectedNetwork || 'Unknown';
            }
            
            // Update connect/disconnect button
            const connectButton = document.getElementById('wallet-connect-btn');
            if (connectButton) {
                if (this.currentStatus === this.connectionStatus.CONNECTED) {
                    connectButton.textContent = 'Disconnect';
                    connectButton.onclick = () => this.disconnect();
                } else {
                    connectButton.textContent = 'Connect Wallet';
                    connectButton.onclick = () => this.showWalletModal();
                }
            }
            
        } catch (error) {
            console.error('❌ Error updating wallet UI:', error);
        }
    }
    
    /**
     * Update balance UI
     */
    updateBalanceUI(balance) {
        try {
            const balanceElement = document.getElementById('wallet-balance');
            if (balanceElement) {
                const symbol = this.supportedNetworks[this.connectedNetwork]?.nativeCurrency.symbol || 'ETH';
                balanceElement.textContent = `${balance.toFixed(4)} ${symbol}`;
            }
        } catch (error) {
            console.error('❌ Error updating balance UI:', error);
        }
    }
    
    /**
     * Show wallet connection modal
     */
    showWalletModal() {
        const modal = document.getElementById('wallet-modal');
        if (modal) {
            modal.style.display = 'block';
            modal.classList.add('show');
            
            // Setup wallet option buttons
            const metamaskBtn = document.getElementById('connect-metamask');
            const walletconnectBtn = document.getElementById('connect-walletconnect');
            
            if (metamaskBtn) {
                metamaskBtn.onclick = async () => {
                    modal.style.display = 'none';
                    await this.connectMetaMask();
                };
            }
            
            if (walletconnectBtn) {
                walletconnectBtn.onclick = async () => {
                    modal.style.display = 'none';
                    await this.connectWalletConnect();
                };
            }
        }
    }
    
    /**
     * Get connection info
     */
    getConnectionInfo() {
        return {
            isConnected: this.currentStatus === this.connectionStatus.CONNECTED,
            wallet: this.connectedWallet,
            account: this.connectedAccount,
            network: this.connectedNetwork,
            status: this.currentStatus
        };
    }
    
    /**
     * Get cached balance
     */
    getCachedBalance(tokenAddress = null) {
        const cacheKey = `${this.connectedAccount}_${this.connectedNetwork}_${tokenAddress || 'native'}`;
        const cached = this.balanceCache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < 30000) { // 30 second cache
            return cached;
        }
        
        return null;
    }
    
    /**
     * Refresh balances
     */
    async refreshBalances() {
        this.balanceCache.clear();
        await this.fetchBalances();
    }
    
    /**
     * Get supported networks
     */
    getSupportedNetworks() {
        return Object.keys(this.supportedNetworks);
    }
    
    /**
     * Check if wallet supports network
     */
    isNetworkSupported(networkName) {
        return networkName in this.supportedNetworks;
    }
}

// Global instance
window.walletManager = new WalletIntegrationManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.walletManager.init();
    });
} else {
    window.walletManager.init();
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WalletIntegrationManager;
}