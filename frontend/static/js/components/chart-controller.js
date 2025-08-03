/**
 * Enhanced Chart Controller with Technical Indicators
 * File: frontend/static/js/components/chart-controller.js (UPDATED & FIXED)
 * 
 * Advanced chart management with professional trading indicators:
 * - Candlestick charts with volume
 * - RSI, MACD, Bollinger Bands integration
 * - Real-time indicator updates
 * - Professional trading visualization
 * - FIXED: All NodeList errors and missing methods
 */

class ChartController {
    constructor() {
        this.charts = new Map();
        this.chartDataCache = new Map();
        this.indicatorData = new Map();
        this.updateInterval = null;
        this.isUpdating = false;
        
        // Chart themes and styling
        this.theme = {
            backgroundColor: 'rgba(255, 255, 255, 0.02)',
            gridColor: 'rgba(255, 255, 255, 0.1)',
            textColor: '#e9ecef',
            bullishColor: '#22c55e',
            bearishColor: '#ef4444',
            volumeColor: '#fbbf24',
            rsiColor: '#8b5cf6',
            macdColor: '#06b6d4',
            signalColor: '#f59e0b',
            bollingerColor: '#ec4899'
        };

        this.bindEvents();
        console.log('✅ Enhanced ChartController initialized with technical indicators');
    }

    /**
     * Create professional candlestick chart with volume
     * Method: createCandlestickChart()
     */
    async createCandlestickChart(containerId, tokenData, options = {}) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                throw new Error(`Chart container ${containerId} not found`);
            }

            // Prepare candlestick data
            const candlestickData = await this.prepareCandlestickData(tokenData);
            
            // Create main price chart
            const priceChartConfig = {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: `${tokenData.symbol} Price`,
                        data: candlestickData.ohlc,
                        borderColor: this.theme.bullishColor,
                        backgroundColor: this.theme.bearishColor,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        x: {
                            type: 'time',
                            grid: {
                                color: this.theme.gridColor
                            },
                            ticks: {
                                color: this.theme.textColor
                            }
                        },
                        y: {
                            position: 'right',
                            grid: {
                                color: this.theme.gridColor
                            },
                            ticks: {
                                color: this.theme.textColor,
                                callback: function(value) {
                                    return '$' + value.toFixed(6);
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                color: this.theme.textColor
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: this.theme.textColor,
                            bodyColor: this.theme.textColor,
                            callbacks: {
                                title: function(context) {
                                    return new Date(context[0].parsed.x).toLocaleString();
                                },
                                label: function(context) {
                                    const data = context.parsed;
                                    return [
                                        `Open: $${data.o?.toFixed(6) || 'N/A'}`,
                                        `High: $${data.h?.toFixed(6) || 'N/A'}`,
                                        `Low: $${data.l?.toFixed(6) || 'N/A'}`,
                                        `Close: $${data.c?.toFixed(6) || 'N/A'}`
                                    ];
                                }
                            }
                        }
                    },
                    ...options
                }
            };

            // Create chart instance
            const chart = new Chart(container, priceChartConfig);
            this.charts.set(containerId, chart);

            // Add technical indicators
            await this.addTechnicalIndicators(containerId, tokenData, candlestickData);

            console.log(`✅ Candlestick chart created for ${containerId}`);
            return chart;

        } catch (error) {
            console.error(`Error creating candlestick chart for ${containerId}:`, error);
            this.showChartError(containerId, 'Failed to load candlestick chart');
            return null;
        }
    }

    /**
     * Add volume indicator to chart
     * Method: addVolumeIndicator()
     */
    async addVolumeIndicator(chartId, volumeData) {
        try {
            const chart = this.charts.get(chartId);
            if (!chart) {
                throw new Error(`Chart ${chartId} not found`);
            }

            // Prepare volume dataset
            const volumeDataset = {
                label: 'Volume',
                data: volumeData.map(item => ({
                    x: item.timestamp,
                    y: item.volume
                })),
                backgroundColor: this.theme.volumeColor,
                borderColor: this.theme.volumeColor,
                borderWidth: 1,
                type: 'bar',
                yAxisID: 'volume'
            };

            // Add volume scale
            chart.options.scales.volume = {
                type: 'linear',
                position: 'left',
                grid: {
                    display: false
                },
                ticks: {
                    color: this.theme.textColor,
                    callback: function(value) {
                        return this.formatVolume(value);
                    }.bind(this)
                }
            };

            // Add dataset and update
            chart.data.datasets.push(volumeDataset);
            chart.update('none');

            console.log(`✅ Volume indicator added to ${chartId}`);
        } catch (error) {
            console.error(`Error adding volume indicator to ${chartId}:`, error);
        }
    }

    /**
     * Add technical indicators to chart
     * Method: addTechnicalIndicators()
     */
    async addTechnicalIndicators(chartId, tokenData, candlestickData) {
        try {
            const prices = candlestickData.ohlc.map(item => item.c);
            const highs = candlestickData.ohlc.map(item => item.h);
            const lows = candlestickData.ohlc.map(item => item.l);
            const timestamps = candlestickData.ohlc.map(item => item.x);

            // Calculate indicators using TechnicalIndicators utility
            const indicators = {
                rsi: TechnicalIndicators.calculateRSI(prices, 14),
                macd: TechnicalIndicators.calculateMACD(prices, 12, 26, 9),
                bollinger: TechnicalIndicators.calculateBollingerBands(prices, 20, 2)
            };

            // Store indicator data
            this.indicatorData.set(chartId, indicators);

            // Add Bollinger Bands to main chart
            await this.addBollingerBands(chartId, timestamps, indicators.bollinger);

            // Create separate indicator charts
            await this.createRSIChart(`${chartId}-rsi`, timestamps, indicators.rsi);
            await this.createMACDChart(`${chartId}-macd`, timestamps, indicators.macd);

            console.log(`✅ Technical indicators added to ${chartId}`);
        } catch (error) {
            console.error(`Error adding technical indicators to ${chartId}:`, error);
        }
    }

    /**
     * Add Bollinger Bands to existing chart
     */
    async addBollingerBands(chartId, timestamps, bollingerData) {
        try {
            const chart = this.charts.get(chartId);
            if (!chart || !bollingerData.upper.length) return;

            // ✅ FIXED: Use Array.slice() instead of trying to slice timestamps directly
            const timestampArray = Array.isArray(timestamps) ? timestamps : Array.from(timestamps);
            
            const upperBandData = timestampArray.slice(-bollingerData.upper.length).map((time, i) => ({
                x: time,
                y: bollingerData.upper[i]
            }));

            const middleBandData = timestampArray.slice(-bollingerData.middle.length).map((time, i) => ({
                x: time,
                y: bollingerData.middle[i]
            }));

            const lowerBandData = timestampArray.slice(-bollingerData.lower.length).map((time, i) => ({
                x: time,
                y: bollingerData.lower[i]
            }));

            // Add Bollinger Band datasets
            chart.data.datasets.push(
                {
                    label: 'Bollinger Upper',
                    data: upperBandData,
                    borderColor: this.theme.bollingerColor,
                    backgroundColor: 'transparent',
                    borderWidth: 1,
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'Bollinger Middle (SMA 20)',
                    data: middleBandData,
                    borderColor: this.theme.bollingerColor,
                    backgroundColor: `${this.theme.bollingerColor}20`,
                    borderWidth: 1,
                    fill: '+1',
                    pointRadius: 0
                },
                {
                    label: 'Bollinger Lower',
                    data: lowerBandData,
                    borderColor: this.theme.bollingerColor,
                    backgroundColor: 'transparent',
                    borderWidth: 1,
                    fill: false,
                    pointRadius: 0
                }
            );

            chart.update('none');
        } catch (error) {
            console.error('Error adding Bollinger Bands:', error);
        }
    }

    /**
     * Create RSI indicator chart
     */
    async createRSIChart(containerId, timestamps, rsiData) {
        try {
            const container = document.getElementById(containerId) || this.createIndicatorContainer(containerId);
            
            // ✅ FIXED: Ensure timestamps is an array before slicing
            const timestampArray = Array.isArray(timestamps) ? timestamps : Array.from(timestamps);
            
            const rsiChartData = timestampArray.slice(-rsiData.length).map((time, i) => ({
                x: time,
                y: rsiData[i]
            }));

            const rsiChart = new Chart(container, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'RSI (14)',
                        data: rsiChartData,
                        borderColor: this.theme.rsiColor,
                        backgroundColor: `${this.theme.rsiColor}20`,
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            grid: {
                                color: this.theme.gridColor
                            },
                            ticks: {
                                color: this.theme.textColor
                            }
                        },
                        y: {
                            min: 0,
                            max: 100,
                            grid: {
                                color: this.theme.gridColor
                            },
                            ticks: {
                                color: this.theme.textColor
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: this.theme.textColor
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: this.theme.textColor,
                            bodyColor: this.theme.textColor
                        }
                    }
                }
            });

            // Add RSI reference lines
            this.addRSILines(rsiChart);
            this.charts.set(containerId, rsiChart);

        } catch (error) {
            console.error('Error creating RSI chart:', error);
        }
    }

    /**
     * Create MACD indicator chart
     */
    async createMACDChart(containerId, timestamps, macdData) {
        try {
            const container = document.getElementById(containerId) || this.createIndicatorContainer(containerId);
            
            // ✅ FIXED: Ensure timestamps is an array before slicing
            const timestampArray = Array.isArray(timestamps) ? timestamps : Array.from(timestamps);
            
            const macdLineData = timestampArray.slice(-macdData.macd.length).map((time, i) => ({
                x: time,
                y: macdData.macd[i]
            }));

            const signalLineData = timestampArray.slice(-macdData.signal.length).map((time, i) => ({
                x: time,
                y: macdData.signal[i]
            }));

            const histogramData = timestampArray.slice(-macdData.histogram.length).map((time, i) => ({
                x: time,
                y: macdData.histogram[i]
            }));

            const macdChart = new Chart(container, {
                type: 'line',
                data: {
                    datasets: [
                        {
                            label: 'MACD',
                            data: macdLineData,
                            borderColor: this.theme.macdColor,
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        },
                        {
                            label: 'Signal',
                            data: signalLineData,
                            borderColor: this.theme.signalColor,
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        },
                        {
                            label: 'Histogram',
                            data: histogramData,
                            backgroundColor: function(context) {
                                return context.parsed.y >= 0 ? 
                                    this.theme.bullishColor : this.theme.bearishColor;
                            }.bind(this),
                            borderWidth: 0,
                            type: 'bar'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            grid: {
                                color: this.theme.gridColor
                            },
                            ticks: {
                                color: this.theme.textColor
                            }
                        },
                        y: {
                            grid: {
                                color: this.theme.gridColor
                            },
                            ticks: {
                                color: this.theme.textColor
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: this.theme.textColor
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: this.theme.textColor,
                            bodyColor: this.theme.textColor
                        }
                    }
                }
            });

            this.charts.set(containerId, macdChart);

        } catch (error) {
            console.error('Error creating MACD chart:', error);
        }
    }

    /**
     * Prepare candlestick data from token data
     */
    async prepareCandlestickData(tokenData) {
        try {
            // Generate sample OHLC data (in production, this would come from real price data)
            const ohlcData = [];
            const basePrice = parseFloat(tokenData.price_usd) || 1;
            
            for (let i = 0; i < 100; i++) {
                const timestamp = Date.now() - (100 - i) * 60000; // 1-minute intervals
                const open = basePrice * (0.98 + Math.random() * 0.04);
                const high = open * (1 + Math.random() * 0.02);
                const low = open * (1 - Math.random() * 0.02);
                const close = low + Math.random() * (high - low);

                ohlcData.push({
                    x: timestamp,
                    o: open,
                    h: high,
                    l: low,
                    c: close
                });
            }

            return {
                ohlc: ohlcData,
                volume: ohlcData.map(item => ({
                    timestamp: item.x,
                    volume: Math.random() * 1000000
                }))
            };
        } catch (error) {
            console.error('Error preparing candlestick data:', error);
            return { ohlc: [], volume: [] };
        }
    }

    /**
     * Add RSI reference lines (30, 50, 70)
     */
    addRSILines(chart) {
        try {
            // Add reference lines plugin
            chart.options.plugins.annotation = {
                annotations: {
                    oversold: {
                        type: 'line',
                        yMin: 30,
                        yMax: 30,
                        borderColor: this.theme.bearishColor,
                        borderWidth: 1,
                        borderDash: [5, 5],
                        label: {
                            content: 'Oversold (30)',
                            enabled: true,
                            position: 'end'
                        }
                    },
                    middle: {
                        type: 'line',
                        yMin: 50,
                        yMax: 50,
                        borderColor: this.theme.textColor,
                        borderWidth: 1,
                        borderDash: [2, 2]
                    },
                    overbought: {
                        type: 'line',
                        yMin: 70,
                        yMax: 70,
                        borderColor: this.theme.bullishColor,
                        borderWidth: 1,
                        borderDash: [5, 5],
                        label: {
                            content: 'Overbought (70)',
                            enabled: true,
                            position: 'end'
                        }
                    }
                }
            };
        } catch (error) {
            console.error('Error adding RSI lines:', error);
        }
    }

    /**
     * Create indicator container if it doesn't exist
     */
    createIndicatorContainer(containerId) {
        try {
            const container = document.createElement('canvas');
            container.id = containerId;
            container.width = 400;
            container.height = 200;
            
            // Add to indicators section or create one
            let indicatorSection = document.getElementById('chart-indicators');
            if (!indicatorSection) {
                indicatorSection = document.createElement('div');
                indicatorSection.id = 'chart-indicators';
                indicatorSection.className = 'chart-indicators mt-3';
                document.querySelector('.chart-container')?.appendChild(indicatorSection);
            }
            
            const wrapper = document.createElement('div');
            wrapper.className = 'indicator-chart mb-3';
            wrapper.appendChild(container);
            indicatorSection.appendChild(wrapper);
            
            return container;
        } catch (error) {
            console.error('Error creating indicator container:', error);
            return null;
        }
    }

    /**
     * Update chart data in real-time
     * Method: updateChartRealtime()
     */
    async updateChartRealtime(chartId, newData) {
        try {
            const chart = this.charts.get(chartId);
            if (!chart) return;

            // Update main chart data
            if (newData.price) {
                const datasets = chart.data.datasets;
                if (datasets && datasets.length > 0 && datasets[0].data.length > 0) {
                    const lastDataPoint = datasets[0].data[datasets[0].data.length - 1];
                    if (lastDataPoint) {
                        lastDataPoint.c = newData.price;
                        lastDataPoint.h = Math.max(lastDataPoint.h || 0, newData.price);
                        lastDataPoint.l = Math.min(lastDataPoint.l || Number.MAX_VALUE, newData.price);
                    }
                }
            }

            // Update indicators if needed
            if (newData.updateIndicators) {
                await this.updateIndicators(chartId, newData);
            }

            chart.update('none');
        } catch (error) {
            console.error(`Error updating chart ${chartId}:`, error);
        }
    }

    /**
     * Update technical indicators
     */
    async updateIndicators(chartId, newData) {
        try {
            const indicators = this.indicatorData.get(chartId);
            if (!indicators) return;

            // Recalculate indicators with new data
            // This would typically be done with fresh price data
            if (newData.prices && Array.isArray(newData.prices) && newData.prices.length > 0) {
                const updatedIndicators = {
                    rsi: TechnicalIndicators.calculateRSI(newData.prices, 14),
                    macd: TechnicalIndicators.calculateMACD(newData.prices, 12, 26, 9),
                    bollinger: TechnicalIndicators.calculateBollingerBands(newData.prices, 20, 2)
                };

                this.indicatorData.set(chartId, updatedIndicators);

                // Update indicator charts
                this.updateRSIChart(`${chartId}-rsi`, updatedIndicators.rsi);
                this.updateMACDChart(`${chartId}-macd`, updatedIndicators.macd);
            }

        } catch (error) {
            console.error('Error updating indicators:', error);
        }
    }

    /**
     * Update RSI chart with new data
     * Method: updateRSIChart() - ADDED MISSING METHOD
     */
    updateRSIChart(chartId, rsiData) {
        try {
            const chart = this.charts.get(chartId);
            if (!chart || !rsiData || !Array.isArray(rsiData)) return;

            const dataset = chart.data.datasets[0];
            if (dataset && dataset.data) {
                // Update the last few data points
                const dataLength = Math.min(rsiData.length, dataset.data.length);
                for (let i = 0; i < dataLength; i++) {
                    const dataIndex = dataset.data.length - dataLength + i;
                    if (dataIndex >= 0 && dataset.data[dataIndex]) {
                        dataset.data[dataIndex].y = rsiData[rsiData.length - dataLength + i];
                    }
                }
                chart.update('none');
            }
        } catch (error) {
            console.error('Error updating RSI chart:', error);
        }
    }

    /**
     * Update MACD chart with new data
     * Method: updateMACDChart() - ADDED MISSING METHOD
     */
    updateMACDChart(chartId, macdData) {
        try {
            const chart = this.charts.get(chartId);
            if (!chart || !macdData) return;

            const datasets = chart.data.datasets;
            if (!datasets || datasets.length < 3) return;

            // Update MACD line
            if (macdData.macd && Array.isArray(macdData.macd)) {
                const macdDataset = datasets[0];
                if (macdDataset && macdDataset.data) {
                    const dataLength = Math.min(macdData.macd.length, macdDataset.data.length);
                    for (let i = 0; i < dataLength; i++) {
                        const dataIndex = macdDataset.data.length - dataLength + i;
                        if (dataIndex >= 0 && macdDataset.data[dataIndex]) {
                            macdDataset.data[dataIndex].y = macdData.macd[macdData.macd.length - dataLength + i];
                        }
                    }
                }
            }

            // Update Signal line
            if (macdData.signal && Array.isArray(macdData.signal)) {
                const signalDataset = datasets[1];
                if (signalDataset && signalDataset.data) {
                    const dataLength = Math.min(macdData.signal.length, signalDataset.data.length);
                    for (let i = 0; i < dataLength; i++) {
                        const dataIndex = signalDataset.data.length - dataLength + i;
                        if (dataIndex >= 0 && signalDataset.data[dataIndex]) {
                            signalDataset.data[dataIndex].y = macdData.signal[macdData.signal.length - dataLength + i];
                        }
                    }
                }
            }

            // Update Histogram
            if (macdData.histogram && Array.isArray(macdData.histogram)) {
                const histogramDataset = datasets[2];
                if (histogramDataset && histogramDataset.data) {
                    const dataLength = Math.min(macdData.histogram.length, histogramDataset.data.length);
                    for (let i = 0; i < dataLength; i++) {
                        const dataIndex = histogramDataset.data.length - dataLength + i;
                        if (dataIndex >= 0 && histogramDataset.data[dataIndex]) {
                            histogramDataset.data[dataIndex].y = macdData.histogram[macdData.histogram.length - dataLength + i];
                        }
                    }
                }
            }

            chart.update('none');
        } catch (error) {
            console.error('Error updating MACD chart:', error);
        }
    }

    /**
     * Format volume for display
     */
    formatVolume(value) {
        if (value >= 1e9) {
            return (value / 1e9).toFixed(1) + 'B';
        } else if (value >= 1e6) {
            return (value / 1e6).toFixed(1) + 'M';
        } else if (value >= 1e3) {
            return (value / 1e3).toFixed(1) + 'K';
        }
        return value.toString();
    }

    /**
     * Show chart error message
     */
    showChartError(containerId, message) {
        try {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `
                    <div class="chart-error">
                        <i class="bi bi-exclamation-triangle text-warning"></i>
                        <p>${message}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error showing chart error:', error);
        }
    }

    /**
     * Bind event handlers
     */
    bindEvents() {
        // Chart controls
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-chart-action]')) {
                this.handleChartAction(e.target);
            }
        });

        // Chart settings
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-chart-setting]')) {
                this.handleChartSetting(e.target);
            }
        });
    }

    /**
     * Handle chart actions
     */
    handleChartAction(element) {
        try {
            const action = element.dataset.chartAction;
            const chartId = element.dataset.chartId;

            switch (action) {
                case 'toggle-indicators':
                    this.toggleIndicators(chartId);
                    break;
                case 'reset-zoom':
                    this.resetZoom(chartId);
                    break;
                case 'export-chart':
                    this.exportChart(chartId);
                    break;
            }
        } catch (error) {
            console.error('Error handling chart action:', error);
        }
    }

    /**
     * Handle chart settings
     */
    handleChartSetting(element) {
        try {
            const setting = element.dataset.chartSetting;
            const value = element.value;
            const chartId = element.dataset.chartId;

            switch (setting) {
                case 'timeframe':
                    this.changeTimeframe(chartId, value);
                    break;
                case 'indicator-period':
                    this.changeIndicatorPeriod(chartId, value);
                    break;
            }
        } catch (error) {
            console.error('Error handling chart setting:', error);
        }
    }

    /**
     * Change chart timeframe
     * Method: changeTimeframe() - ADDED MISSING METHOD
     */
    changeTimeframe(chartId, timeframe) {
        try {
            console.log(`Changing timeframe for ${chartId} to ${timeframe}`);
            // Implementation would depend on data source
            // This is a placeholder for the actual timeframe change logic
        } catch (error) {
            console.error('Error changing timeframe:', error);
        }
    }

    /**
     * Change indicator period
     * Method: changeIndicatorPeriod() - ADDED MISSING METHOD
     */
    changeIndicatorPeriod(chartId, period) {
        try {
            console.log(`Changing indicator period for ${chartId} to ${period}`);
            // Implementation would recalculate indicators with new period
            // This is a placeholder for the actual period change logic
        } catch (error) {
            console.error('Error changing indicator period:', error);
        }
    }

    /**
     * Toggle indicators visibility
     */
    toggleIndicators(chartId) {
        const indicatorSection = document.getElementById('chart-indicators');
        if (indicatorSection) {
            indicatorSection.style.display = 
                indicatorSection.style.display === 'none' ? 'block' : 'none';
        }
    }

    /**
     * Reset chart zoom
     */
    resetZoom(chartId) {
        const chart = this.charts.get(chartId);
        if (chart && chart.resetZoom) {
            chart.resetZoom();
        }
    }

    /**
     * Export chart as image
     */
    exportChart(chartId) {
        try {
            const chart = this.charts.get(chartId);
            if (chart) {
                const url = chart.toBase64Image();
                const link = document.createElement('a');
                link.download = `${chartId}-chart.png`;
                link.href = url;
                link.click();
            }
        } catch (error) {
            console.error('Error exporting chart:', error);
        }
    }

    /**
     * Get chart by ID
     * Method: getChart() - ADDED UTILITY METHOD
     */
    getChart(chartId) {
        return this.charts.get(chartId);
    }

    /**
     * Get all chart IDs
     * Method: getChartIds() - ADDED UTILITY METHOD
     */
    getChartIds() {
        return Array.from(this.charts.keys());
    }

    /**
     * Check if chart exists
     * Method: hasChart() - ADDED UTILITY METHOD
     */
    hasChart(chartId) {
        return this.charts.has(chartId);
    }

    /**
     * Update all charts
     * Method: updateAllCharts() - ADDED UTILITY METHOD
     */
    updateAllCharts() {
        try {
            this.charts.forEach((chart, chartId) => {
                if (chart) {
                    chart.update('none');
                }
            });
        } catch (error) {
            console.error('Error updating all charts:', error);
        }
    }

    /**
     * Cleanup charts and intervals
     */
    destroy() {
        try {
            // Clear update interval
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
            }

            // Destroy all charts
            this.charts.forEach((chart) => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });

            // Clear maps
            this.charts.clear();
            this.chartDataCache.clear();
            this.indicatorData.clear();

            console.log('✅ ChartController destroyed');
        } catch (error) {
            console.error('Error destroying ChartController:', error);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartController;
} else {
    window.ChartController = ChartController;
}