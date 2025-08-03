/**
 * Chart Controller Module
 * File: frontend/static/js/components/chart-controller.js
 * 
 * Professional Chart.js integration for DEX Sniper Pro.
 * Handles price charts, portfolio analytics, and trading visualizations.
 */

class ChartController {
    constructor(app) {
        this.app = app;
        this.isInitialized = false;
        this.charts = new Map();
        this.chartDefaults = {};
        
        // Chart configuration
        this.config = {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: true,
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    grid: {
                        display: true,
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        };
        
        console.log('📊 Chart Controller created');
    }

    /**
     * Initialize Chart Controller
     */
    async init() {
        try {
            console.log('🔧 Initializing Chart Controller...');
            
            // Check if Chart.js is available
            if (typeof Chart === 'undefined') {
                console.warn('⚠️ Chart.js not loaded, loading from CDN...');
                await this.loadChartJS();
            }
            
            // Configure Chart.js defaults
            this.configureChartDefaults();
            
            // Initialize existing chart containers
            this.initializeChartContainers();
            
            // Setup event listeners
            this.setupEventListeners();
            
            this.isInitialized = true;
            console.log('✅ Chart Controller initialized');
            
            // Emit initialization event
            this.app.events.dispatchEvent(new CustomEvent('charts:initialized'));
            
        } catch (error) {
            console.error('❌ Chart Controller initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load Chart.js library dynamically
     */
    async loadChartJS() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.min.js';
            script.integrity = 'sha512-7U4rRB8aGAHGVad3u2jiC7GA5/1YhQcQjxKeaVms/bT66i3LVBMRcBI9KwABNWnxOSwulkuSXxZLGuyfvo7V0A==';
            script.crossOrigin = 'anonymous';
            script.onload = () => {
                console.log('✅ Chart.js loaded successfully');
                resolve();
            };
            script.onerror = (error) => {
                console.error('❌ Failed to load Chart.js:', error);
                reject(new Error('Failed to load Chart.js library'));
            };
            document.head.appendChild(script);
        });
    }

    /**
     * Configure Chart.js global defaults
     */
    configureChartDefaults() {
        try {
            if (typeof Chart !== 'undefined') {
                // Set global defaults
                Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
                Chart.defaults.font.size = 12;
                Chart.defaults.color = '#6c757d';
                Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
                Chart.defaults.backgroundColor = 'rgba(13, 202, 240, 0.1)';
                
                // Register custom plugins if needed
                this.registerCustomPlugins();
                
                console.log('✅ Chart.js defaults configured');
            }
        } catch (error) {
            console.error('❌ Failed to configure Chart.js defaults:', error);
        }
    }

    /**
     * Register custom Chart.js plugins
     */
    registerCustomPlugins() {
        try {
            // Custom plugin for dark theme support
            const darkThemePlugin = {
                id: 'darkTheme',
                beforeDraw: (chart) => {
                    if (document.documentElement.getAttribute('data-bs-theme') === 'dark') {
                        chart.options.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';
                        chart.options.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';
                        Chart.defaults.color = '#adb5bd';
                    } else {
                        chart.options.scales.x.grid.color = 'rgba(0, 0, 0, 0.1)';
                        chart.options.scales.y.grid.color = 'rgba(0, 0, 0, 0.1)';
                        Chart.defaults.color = '#6c757d';
                    }
                }
            };
            
            Chart.register(darkThemePlugin);
            
        } catch (error) {
            console.error('❌ Failed to register custom plugins:', error);
        }
    }

    /**
     * Initialize existing chart containers
     */
    initializeChartContainers() {
        try {
            const chartContainers = document.querySelectorAll('[data-chart-type]');
            
            chartContainers.forEach(container => {
                const chartType = container.getAttribute('data-chart-type');
                const chartId = container.id || `chart_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                
                if (!container.id) {
                    container.id = chartId;
                }
                
                console.log(`📊 Found chart container: ${chartId} (${chartType})`);
                
                // Initialize chart based on type
                this.initializeChart(chartId, chartType);
            });
            
        } catch (error) {
            console.error('❌ Failed to initialize chart containers:', error);
        }
    }

    /**
     * Initialize specific chart
     */
    initializeChart(chartId, chartType, data = null, options = {}) {
        try {
            const canvas = document.getElementById(chartId);
            if (!canvas) {
                console.error(`❌ Chart canvas not found: ${chartId}`);
                return null;
            }

            const ctx = canvas.getContext('2d');
            
            // Merge default config with custom options
            const chartConfig = this.getChartConfig(chartType, data, options);
            
            // Create chart
            const chart = new Chart(ctx, chartConfig);
            
            // Store chart reference
            this.charts.set(chartId, {
                chart,
                type: chartType,
                canvas,
                lastUpdate: new Date()
            });
            
            console.log(`✅ Chart initialized: ${chartId} (${chartType})`);
            return chart;
            
        } catch (error) {
            console.error(`❌ Failed to initialize chart ${chartId}:`, error);
            return null;
        }
    }

    /**
     * Get chart configuration by type
     */
    getChartConfig(chartType, data = null, customOptions = {}) {
        const baseConfig = {
            responsive: true,
            maintainAspectRatio: false,
            ...this.config
        };

        switch (chartType) {
            case 'price':
                return this.getPriceChartConfig(data, customOptions, baseConfig);
            
            case 'portfolio':
                return this.getPortfolioChartConfig(data, customOptions, baseConfig);
            
            case 'volume':
                return this.getVolumeChartConfig(data, customOptions, baseConfig);
            
            case 'risk':
                return this.getRiskChartConfig(data, customOptions, baseConfig);
            
            case 'doughnut':
                return this.getDoughnutChartConfig(data, customOptions, baseConfig);
            
            case 'bar':
                return this.getBarChartConfig(data, customOptions, baseConfig);
            
            default:
                return this.getDefaultChartConfig(data, customOptions, baseConfig);
        }
    }

    /**
     * Price chart configuration
     */
    getPriceChartConfig(data, customOptions, baseConfig) {
        return {
            type: 'line',
            data: data || {
                labels: [],
                datasets: [{
                    label: 'Price',
                    data: [],
                    borderColor: '#0dcaf0',
                    backgroundColor: 'rgba(13, 202, 240, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...baseConfig,
                scales: {
                    x: {
                        ...baseConfig.scales.x,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        ...baseConfig.scales.y,
                        title: {
                            display: true,
                            text: 'Price ($)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(6);
                            }
                        }
                    }
                },
                plugins: {
                    ...baseConfig.plugins,
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: $${context.parsed.y.toFixed(6)}`;
                            }
                        }
                    }
                },
                ...customOptions
            }
        };
    }

    /**
     * Portfolio chart configuration
     */
    getPortfolioChartConfig(data, customOptions, baseConfig) {
        return {
            type: 'line',
            data: data || {
                labels: [],
                datasets: [{
                    label: 'Portfolio Value',
                    data: [],
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'P&L',
                    data: [],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                }]
            },
            options: {
                ...baseConfig,
                scales: {
                    x: {
                        ...baseConfig.scales.x,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        ...baseConfig.scales.y,
                        title: {
                            display: true,
                            text: 'Value ($)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    ...baseConfig.plugins,
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                ...customOptions
            }
        };
    }

    /**
     * Volume chart configuration
     */
    getVolumeChartConfig(data, customOptions, baseConfig) {
        return {
            type: 'bar',
            data: data || {
                labels: [],
                datasets: [{
                    label: 'Volume',
                    data: [],
                    backgroundColor: 'rgba(255, 193, 7, 0.6)',
                    borderColor: '#ffc107',
                    borderWidth: 1
                }]
            },
            options: {
                ...baseConfig,
                scales: {
                    x: {
                        ...baseConfig.scales.x,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        ...baseConfig.scales.y,
                        title: {
                            display: true,
                            text: 'Volume ($)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    ...baseConfig.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Volume: $${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                ...customOptions
            }
        };
    }

    /**
     * Risk analysis chart configuration
     */
    getRiskChartConfig(data, customOptions, baseConfig) {
        return {
            type: 'radar',
            data: data || {
                labels: ['Liquidity', 'Volume', 'Holders', 'Contract', 'Social', 'Technical'],
                datasets: [{
                    label: 'Risk Score',
                    data: [0, 0, 0, 0, 0, 0],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.2)',
                    borderWidth: 2,
                    pointBackgroundColor: '#dc3545'
                }]
            },
            options: {
                ...baseConfig,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                },
                plugins: {
                    ...baseConfig.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed.r}/100`;
                            }
                        }
                    }
                },
                ...customOptions
            }
        };
    }

    /**
     * Doughnut chart configuration
     */
    getDoughnutChartConfig(data, customOptions, baseConfig) {
        return {
            type: 'doughnut',
            data: data || {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#0dcaf0',
                        '#198754',
                        '#ffc107',
                        '#dc3545',
                        '#6f42c1',
                        '#fd7e14'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                ...baseConfig,
                plugins: {
                    ...baseConfig.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${percentage}%`;
                            }
                        }
                    }
                },
                ...customOptions
            }
        };
    }

    /**
     * Bar chart configuration
     */
    getBarChartConfig(data, customOptions, baseConfig) {
        return {
            type: 'bar',
            data: data || {
                labels: [],
                datasets: [{
                    label: 'Value',
                    data: [],
                    backgroundColor: 'rgba(13, 202, 240, 0.6)',
                    borderColor: '#0dcaf0',
                    borderWidth: 1
                }]
            },
            options: {
                ...baseConfig,
                ...customOptions
            }
        };
    }

    /**
     * Default chart configuration
     */
    getDefaultChartConfig(data, customOptions, baseConfig) {
        return {
            type: 'line',
            data: data || {
                labels: [],
                datasets: [{
                    label: 'Data',
                    data: [],
                    borderColor: '#0dcaf0',
                    backgroundColor: 'rgba(13, 202, 240, 0.1)',
                    borderWidth: 2
                }]
            },
            options: {
                ...baseConfig,
                ...customOptions
            }
        };
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        try {
            // Listen for theme changes
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'data-bs-theme') {
                        this.updateChartsForTheme();
                    }
                });
            });
            
            observer.observe(document.documentElement, {
                attributes: true,
                attributeFilter: ['data-bs-theme']
            });
            
            // Listen for window resize
            window.addEventListener('resize', this.debounce(() => {
                this.resizeAllCharts();
            }, 250));
            
            console.log('✅ Chart event listeners setup');
            
        } catch (error) {
            console.error('❌ Failed to setup chart event listeners:', error);
        }
    }

    // Chart Management Methods

    /**
     * Create new chart
     */
    createChart(containerId, chartType, data = null, options = {}) {
        try {
            return this.initializeChart(containerId, chartType, data, options);
        } catch (error) {
            console.error(`❌ Failed to create chart ${containerId}:`, error);
            return null;
        }
    }

    /**
     * Update chart data
     */
    updateChart(chartId, newData, animate = true) {
        try {
            const chartInfo = this.charts.get(chartId);
            if (!chartInfo) {
                console.warn(`⚠️ Chart not found: ${chartId}`);
                return false;
            }

            const chart = chartInfo.chart;
            
            // Update data
            if (newData.labels) {
                chart.data.labels = newData.labels;
            }
            
            if (newData.datasets) {
                chart.data.datasets = newData.datasets;
            }
            
            // Update chart
            chart.update(animate ? 'active' : 'none');
            
            // Update last update time
            chartInfo.lastUpdate = new Date();
            
            console.log(`✅ Chart updated: ${chartId}`);
            return true;
            
        } catch (error) {
            console.error(`❌ Failed to update chart ${chartId}:`, error);
            return false;
        }
    }

    /**
     * Add data point to chart
     */
    addDataPoint(chartId, label, datasetIndex = 0, value, maxPoints = 50) {
        try {
            const chartInfo = this.charts.get(chartId);
            if (!chartInfo) {
                console.warn(`⚠️ Chart not found: ${chartId}`);
                return false;
            }

            const chart = chartInfo.chart;
            
            // Add label
            chart.data.labels.push(label);
            
            // Add data point
            if (chart.data.datasets[datasetIndex]) {
                chart.data.datasets[datasetIndex].data.push(value);
                
                // Limit data points
                if (chart.data.labels.length > maxPoints) {
                    chart.data.labels.shift();
                    chart.data.datasets[datasetIndex].data.shift();
                }
            }
            
            // Update chart
            chart.update('active');
            
            return true;
            
        } catch (error) {
            console.error(`❌ Failed to add data point to chart ${chartId}:`, error);
            return false;
        }
    }

    /**
     * Destroy chart
     */
    destroyChart(chartId) {
        try {
            const chartInfo = this.charts.get(chartId);
            if (!chartInfo) {
                console.warn(`⚠️ Chart not found: ${chartId}`);
                return false;
            }

            chartInfo.chart.destroy();
            this.charts.delete(chartId);
            
            console.log(`✅ Chart destroyed: ${chartId}`);
            return true;
            
        } catch (error) {
            console.error(`❌ Failed to destroy chart ${chartId}:`, error);
            return false;
        }
    }

    /**
     * Resize all charts
     */
    resizeAllCharts() {
        try {
            this.charts.forEach((chartInfo, chartId) => {
                chartInfo.chart.resize();
            });
            
        } catch (error) {
            console.error('❌ Failed to resize charts:', error);
        }
    }

    /**
     * Update charts for theme change
     */
    updateChartsForTheme() {
        try {
            this.charts.forEach((chartInfo, chartId) => {
                chartInfo.chart.update('none');
            });
            
        } catch (error) {
            console.error('❌ Failed to update charts for theme:', error);
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
     * Generate sample data for testing
     */
    generateSampleData(type = 'price', points = 20) {
        const labels = [];
        const data = [];
        
        for (let i = 0; i < points; i++) {
            const date = new Date();
            date.setMinutes(date.getMinutes() - (points - i) * 5);
            labels.push(date.toLocaleTimeString());
            
            switch (type) {
                case 'price':
                    data.push((Math.random() * 100 + 50).toFixed(6));
                    break;
                case 'volume':
                    data.push(Math.floor(Math.random() * 1000000));
                    break;
                default:
                    data.push(Math.random() * 100);
            }
        }
        
        return { labels, data };
    }

    // Public API Methods

    /**
     * Get chart instance
     */
    getChart(chartId) {
        const chartInfo = this.charts.get(chartId);
        return chartInfo ? chartInfo.chart : null;
    }

    /**
     * Get all charts
     */
    getAllCharts() {
        const result = {};
        this.charts.forEach((chartInfo, chartId) => {
            result[chartId] = {
                chart: chartInfo.chart,
                type: chartInfo.type,
                lastUpdate: chartInfo.lastUpdate
            };
        });
        return result;
    }

    /**
     * Check if Chart.js is available
     */
    isChartJSAvailable() {
        return typeof Chart !== 'undefined';
    }

    /**
     * Get controller status
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            chartCount: this.charts.size,
            chartJSAvailable: this.isChartJSAvailable(),
            charts: Array.from(this.charts.keys())
        };
    }

    /**
     * Cleanup resources
     */
    destroy() {
        try {
            console.log('🧹 Cleaning up Chart Controller...');
            
            // Destroy all charts
            this.charts.forEach((chartInfo, chartId) => {
                chartInfo.chart.destroy();
            });
            
            this.charts.clear();
            this.isInitialized = false;
            
            console.log('✅ Chart Controller cleaned up');
            
        } catch (error) {
            console.error('❌ Failed to cleanup Chart Controller:', error);
        }
    }
}

// Export for global use
window.ChartController = ChartController;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartController;
}

console.log('📊 Chart Controller module loaded successfully');