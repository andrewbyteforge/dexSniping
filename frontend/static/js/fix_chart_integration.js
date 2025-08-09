/**
 * Chart Integration Fix
 * File: frontend/static/js/fix_chart_integration.js
 * 
 * Fixes the Chart.js integration issues and module loading conflicts
 * in the DEX Sniper Pro dashboard application.
 */

/**
 * Chart Manager - Handles Chart.js initialization and global access
 */
class ChartManager {
    constructor() {
        this.isInitialized = false;
        this.charts = new Map();
        this.chartDefaults = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };
        
        console.log('📊 Chart Manager created');
    }

    /**
     * Initialize Chart.js and setup global access
     */
    async init() {
        try {
            // Wait for Chart.js to be available
            await this.waitForChart();
            
            // Setup global configuration
            this.setupGlobalConfig();
            
            this.isInitialized = true;
            console.log('✅ Chart Manager initialized successfully');
            
            return true;
        } catch (error) {
            console.error('❌ Chart Manager initialization failed:', error);
            return false;
        }
    }

    /**
     * Wait for Chart.js to be loaded
     */
    waitForChart() {
        return new Promise((resolve, reject) => {
            const maxAttempts = 50;
            let attempts = 0;
            
            const checkChart = () => {
                attempts++;
                
                if (typeof Chart !== 'undefined' && Chart.Chart) {
                    console.log('✅ Chart.js detected');
                    resolve();
                } else if (attempts >= maxAttempts) {
                    reject(new Error('Chart.js failed to load after maximum attempts'));
                } else {
                    setTimeout(checkChart, 100);
                }
            };
            
            checkChart();
        });
    }

    /**
     * Setup global Chart.js configuration
     */
    setupGlobalConfig() {
        if (typeof Chart !== 'undefined') {
            // Global defaults
            Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
            Chart.defaults.color = '#6c757d';
            Chart.defaults.borderColor = '#dee2e6';
            
            // Register components if needed
            if (Chart.register) {
                Chart.register(
                    Chart.CategoryScale,
                    Chart.LinearScale,
                    Chart.PointElement,
                    Chart.LineElement,
                    Chart.BarElement,
                    Chart.Title,
                    Chart.Tooltip,
                    Chart.Legend
                );
            }
            
            console.log('📊 Chart.js global configuration applied');
        }
    }

    /**
     * Create a performance chart
     */
    createPerformanceChart(canvasId, data = null) {
        try {
            if (!this.isInitialized) {
                throw new Error('Chart Manager not initialized');
            }

            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                throw new Error(`Canvas element ${canvasId} not found`);
            }

            // Destroy existing chart if it exists
            if (this.charts.has(canvasId)) {
                this.destroyChart(canvasId);
            }

            const ctx = canvas.getContext('2d');
            
            const chartData = data || this.generateSamplePerformanceData();
            
            const config = {
                type: 'line',
                data: chartData,
                options: {
                    ...this.chartDefaults,
                    plugins: {
                        ...this.chartDefaults.plugins,
                        title: {
                            display: true,
                            text: 'Portfolio Performance'
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Value ($)'
                            }
                        }
                    }
                }
            };

            const chart = new Chart(ctx, config);
            this.charts.set(canvasId, chart);
            
            console.log(`✅ Performance chart created: ${canvasId}`);
            return chart;
            
        } catch (error) {
            console.error(`❌ Failed to create performance chart:`, error);
            this.showChartError(canvasId, 'Failed to load performance chart');
            return null;
        }
    }

    /**
     * Create a portfolio distribution chart
     */
    createDistributionChart(canvasId, data = null) {
        try {
            if (!this.isInitialized) {
                throw new Error('Chart Manager not initialized');
            }

            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                throw new Error(`Canvas element ${canvasId} not found`);
            }

            if (this.charts.has(canvasId)) {
                this.destroyChart(canvasId);
            }

            const ctx = canvas.getContext('2d');
            
            const chartData = data || this.generateSampleDistributionData();
            
            const config = {
                type: 'doughnut',
                data: chartData,
                options: {
                    ...this.chartDefaults,
                    plugins: {
                        ...this.chartDefaults.plugins,
                        title: {
                            display: true,
                            text: 'Portfolio Distribution'
                        }
                    }
                }
            };

            const chart = new Chart(ctx, config);
            this.charts.set(canvasId, chart);
            
            console.log(`✅ Distribution chart created: ${canvasId}`);
            return chart;
            
        } catch (error) {
            console.error(`❌ Failed to create distribution chart:`, error);
            this.showChartError(canvasId, 'Failed to load distribution chart');
            return null;
        }
    }

    /**
     * Update chart data
     */
    updateChart(canvasId, newData) {
        try {
            const chart = this.charts.get(canvasId);
            if (!chart) {
                console.warn(`Chart ${canvasId} not found for update`);
                return false;
            }

            chart.data = newData;
            chart.update('none'); // Use 'none' animation for better performance
            
            console.log(`📊 Chart ${canvasId} updated`);
            return true;
            
        } catch (error) {
            console.error(`❌ Failed to update chart ${canvasId}:`, error);
            return false;
        }
    }

    /**
     * Destroy a specific chart
     */
    destroyChart(canvasId) {
        try {
            const chart = this.charts.get(canvasId);
            if (chart) {
                chart.destroy();
                this.charts.delete(canvasId);
                console.log(`🗑️ Chart ${canvasId} destroyed`);
            }
        } catch (error) {
            console.error(`❌ Failed to destroy chart ${canvasId}:`, error);
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        try {
            this.charts.forEach((chart, id) => {
                chart.destroy();
            });
            this.charts.clear();
            console.log('🗑️ All charts destroyed');
        } catch (error) {
            console.error('❌ Failed to destroy all charts:', error);
        }
    }

    /**
     * Show error message in chart container
     */
    showChartError(canvasId, message) {
        try {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const container = canvas.parentElement;
                container.innerHTML = `
                    <div class="d-flex align-items-center justify-content-center h-100">
                        <div class="text-center text-muted">
                            <i class="bi bi-exclamation-triangle fs-3 mb-2"></i>
                            <p class="mb-0">${message}</p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Failed to show chart error:', error);
        }
    }

    /**
     * Generate sample performance data
     */
    generateSamplePerformanceData() {
        const labels = [];
        const data = [];
        const now = new Date();
        
        for (let i = 29; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString());
            
            // Generate realistic performance data
            const baseValue = 10000;
            const variation = (Math.random() - 0.5) * 1000;
            data.push(baseValue + variation + (i * 50)); // Slight upward trend
        }

        return {
            labels: labels,
            datasets: [{
                label: 'Portfolio Value',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        };
    }

    /**
     * Generate sample distribution data
     */
    generateSampleDistributionData() {
        return {
            labels: ['Ethereum', 'Bitcoin', 'Solana', 'Polygon', 'Others'],
            datasets: [{
                data: [35, 25, 15, 15, 10],
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#f5576c',
                    '#4facfe'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        };
    }

    /**
     * Get chart instance
     */
    getChart(canvasId) {
        return this.charts.get(canvasId);
    }

    /**
     * Get all chart IDs
     */
    getChartIds() {
        return Array.from(this.charts.keys());
    }

    /**
     * Check if chart exists
     */
    hasChart(canvasId) {
        return this.charts.has(canvasId);
    }
}

/**
 * Dashboard Chart Integration - Main initialization function
 */
async function initializeDashboardCharts() {
    try {
        console.log('🚀 Initializing dashboard charts...');
        
        // Create global chart manager
        window.chartManager = new ChartManager();
        
        // Initialize chart manager
        const success = await window.chartManager.init();
        if (!success) {
            throw new Error('Chart manager initialization failed');
        }
        
        // Initialize charts when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createDashboardCharts);
        } else {
            createDashboardCharts();
        }
        
        console.log('✅ Dashboard chart integration completed');
        
    } catch (error) {
        console.error('❌ Dashboard chart integration failed:', error);
    }
}

/**
 * Create dashboard charts
 */
function createDashboardCharts() {
    try {
        console.log('📊 Creating dashboard charts...');
        
        // Create performance chart if container exists
        if (document.getElementById('performanceChart')) {
            window.chartManager.createPerformanceChart('performanceChart');
        }
        
        // Create distribution chart if container exists  
        if (document.getElementById('distributionChart')) {
            window.chartManager.createDistributionChart('distributionChart');
        }
        
        console.log('✅ Dashboard charts created');
        
    } catch (error) {
        console.error('❌ Failed to create dashboard charts:', error);
    }
}

/**
 * Legacy compatibility function for existing code
 */
function initPerformanceChart() {
    console.log('🔄 Legacy initPerformanceChart called - delegating to chart manager');
    
    if (window.chartManager && window.chartManager.isInitialized) {
        window.chartManager.createPerformanceChart('performanceChart');
    } else {
        console.warn('⚠️ Chart manager not ready, scheduling retry...');
        setTimeout(initPerformanceChart, 500);
    }
}

// Make functions globally available
window.initPerformanceChart = initPerformanceChart;
window.initializeDashboardCharts = initializeDashboardCharts;

// Auto-initialize when script loads
initializeDashboardCharts();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChartManager, initializeDashboardCharts };
}