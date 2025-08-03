/**
 * Technical Indicators Utility Module
 * File: frontend/static/js/utils/technical-indicators.js
 * 
 * Advanced technical analysis calculations for professional trading charts.
 * Implements RSI, MACD, Bollinger Bands, and other key indicators.
 */

class TechnicalIndicators {
    /**
     * Calculate Relative Strength Index (RSI)
     * @param {Array} prices - Array of price values
     * @param {number} period - Period for RSI calculation (default: 14)
     * @returns {Array} RSI values
     */
    static calculateRSI(prices, period = 14) {
        try {
            if (!prices || prices.length < period + 1) {
                throw new Error(`Insufficient data for RSI calculation. Need at least ${period + 1} prices`);
            }

            const rsiValues = [];
            const gains = [];
            const losses = [];

            // Calculate price changes
            for (let i = 1; i < prices.length; i++) {
                const change = prices[i] - prices[i - 1];
                gains.push(change > 0 ? change : 0);
                losses.push(change < 0 ? Math.abs(change) : 0);
            }

            // Calculate initial average gain and loss
            let avgGain = gains.slice(0, period).reduce((sum, gain) => sum + gain, 0) / period;
            let avgLoss = losses.slice(0, period).reduce((sum, loss) => sum + loss, 0) / period;

            // Calculate RSI values
            for (let i = period; i < gains.length; i++) {
                if (i === period) {
                    // First RSI calculation
                    const rs = avgGain / (avgLoss || 0.001); // Avoid division by zero
                    const rsi = 100 - (100 / (1 + rs));
                    rsiValues.push(Math.round(rsi * 100) / 100);
                } else {
                    // Smoothed RSI calculation
                    avgGain = ((avgGain * (period - 1)) + gains[i]) / period;
                    avgLoss = ((avgLoss * (period - 1)) + losses[i]) / period;
                    
                    const rs = avgGain / (avgLoss || 0.001);
                    const rsi = 100 - (100 / (1 + rs));
                    rsiValues.push(Math.round(rsi * 100) / 100);
                }
            }

            return rsiValues;
        } catch (error) {
            console.error('Error calculating RSI:', error);
            return [];
        }
    }

    /**
     * Calculate Moving Average Convergence Divergence (MACD)
     * @param {Array} prices - Array of price values
     * @param {number} fastPeriod - Fast EMA period (default: 12)
     * @param {number} slowPeriod - Slow EMA period (default: 26)
     * @param {number} signalPeriod - Signal line EMA period (default: 9)
     * @returns {Object} MACD line, signal line, and histogram
     */
    static calculateMACD(prices, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
        try {
            if (!prices || prices.length < slowPeriod) {
                throw new Error(`Insufficient data for MACD calculation. Need at least ${slowPeriod} prices`);
            }

            // Calculate EMAs
            const fastEMA = this.calculateEMA(prices, fastPeriod);
            const slowEMA = this.calculateEMA(prices, slowPeriod);

            // Calculate MACD line
            const macdLine = [];
            const startIndex = slowPeriod - 1;
            
            for (let i = 0; i < fastEMA.length; i++) {
                if (i >= startIndex) {
                    macdLine.push(fastEMA[i] - slowEMA[i - (fastPeriod - slowPeriod)]);
                }
            }

            // Calculate signal line (EMA of MACD line)
            const signalLine = this.calculateEMA(macdLine, signalPeriod);

            // Calculate histogram
            const histogram = [];
            const signalStartIndex = signalPeriod - 1;
            
            for (let i = signalStartIndex; i < macdLine.length; i++) {
                histogram.push(macdLine[i] - signalLine[i - signalStartIndex]);
            }

            return {
                macd: macdLine.map(val => Math.round(val * 10000) / 10000),
                signal: signalLine.map(val => Math.round(val * 10000) / 10000),
                histogram: histogram.map(val => Math.round(val * 10000) / 10000)
            };
        } catch (error) {
            console.error('Error calculating MACD:', error);
            return { macd: [], signal: [], histogram: [] };
        }
    }

    /**
     * Calculate Bollinger Bands
     * @param {Array} prices - Array of price values
     * @param {number} period - Period for moving average (default: 20)
     * @param {number} stdDevMultiplier - Standard deviation multiplier (default: 2)
     * @returns {Object} Upper band, middle line (SMA), and lower band
     */
    static calculateBollingerBands(prices, period = 20, stdDevMultiplier = 2) {
        try {
            if (!prices || prices.length < period) {
                throw new Error(`Insufficient data for Bollinger Bands. Need at least ${period} prices`);
            }

            const sma = this.calculateSMA(prices, period);
            const upperBand = [];
            const lowerBand = [];

            for (let i = period - 1; i < prices.length; i++) {
                const priceSlice = prices.slice(i - period + 1, i + 1);
                const average = sma[i - period + 1];
                
                // Calculate standard deviation
                const variance = priceSlice.reduce((sum, price) => {
                    return sum + Math.pow(price - average, 2);
                }, 0) / period;
                
                const stdDev = Math.sqrt(variance);
                
                upperBand.push(Math.round((average + (stdDev * stdDevMultiplier)) * 100) / 100);
                lowerBand.push(Math.round((average - (stdDev * stdDevMultiplier)) * 100) / 100);
            }

            return {
                upper: upperBand,
                middle: sma.map(val => Math.round(val * 100) / 100),
                lower: lowerBand
            };
        } catch (error) {
            console.error('Error calculating Bollinger Bands:', error);
            return { upper: [], middle: [], lower: [] };
        }
    }

    /**
     * Calculate Simple Moving Average (SMA)
     * @param {Array} prices - Array of price values
     * @param {number} period - Period for moving average
     * @returns {Array} SMA values
     */
    static calculateSMA(prices, period) {
        try {
            if (!prices || prices.length < period) {
                throw new Error(`Insufficient data for SMA calculation. Need at least ${period} prices`);
            }

            const smaValues = [];
            
            for (let i = period - 1; i < prices.length; i++) {
                const slice = prices.slice(i - period + 1, i + 1);
                const average = slice.reduce((sum, price) => sum + price, 0) / period;
                smaValues.push(average);
            }

            return smaValues;
        } catch (error) {
            console.error('Error calculating SMA:', error);
            return [];
        }
    }

    /**
     * Calculate Exponential Moving Average (EMA)
     * @param {Array} prices - Array of price values
     * @param {number} period - Period for moving average
     * @returns {Array} EMA values
     */
    static calculateEMA(prices, period) {
        try {
            if (!prices || prices.length < period) {
                throw new Error(`Insufficient data for EMA calculation. Need at least ${period} prices`);
            }

            const emaValues = [];
            const multiplier = 2 / (period + 1);

            // First EMA value is SMA
            let ema = prices.slice(0, period).reduce((sum, price) => sum + price, 0) / period;
            emaValues.push(ema);

            // Calculate subsequent EMA values
            for (let i = period; i < prices.length; i++) {
                ema = (prices[i] * multiplier) + (ema * (1 - multiplier));
                emaValues.push(ema);
            }

            return emaValues;
        } catch (error) {
            console.error('Error calculating EMA:', error);
            return [];
        }
    }

    /**
     * Calculate Stochastic Oscillator
     * @param {Array} highs - Array of high prices
     * @param {Array} lows - Array of low prices
     * @param {Array} closes - Array of closing prices
     * @param {number} kPeriod - %K period (default: 14)
     * @param {number} dPeriod - %D period (default: 3)
     * @returns {Object} %K and %D values
     */
    static calculateStochastic(highs, lows, closes, kPeriod = 14, dPeriod = 3) {
        try {
            if (!highs || !lows || !closes || 
                highs.length !== lows.length || 
                lows.length !== closes.length || 
                closes.length < kPeriod) {
                throw new Error('Invalid data for Stochastic calculation');
            }

            const kValues = [];

            for (let i = kPeriod - 1; i < closes.length; i++) {
                const highestHigh = Math.max(...highs.slice(i - kPeriod + 1, i + 1));
                const lowestLow = Math.min(...lows.slice(i - kPeriod + 1, i + 1));
                const currentClose = closes[i];

                const k = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;
                kValues.push(Math.round(k * 100) / 100);
            }

            // Calculate %D (SMA of %K)
            const dValues = this.calculateSMA(kValues, dPeriod);

            return {
                k: kValues,
                d: dValues
            };
        } catch (error) {
            console.error('Error calculating Stochastic:', error);
            return { k: [], d: [] };
        }
    }

    /**
     * Calculate Average True Range (ATR)
     * @param {Array} highs - Array of high prices
     * @param {Array} lows - Array of low prices
     * @param {Array} closes - Array of closing prices
     * @param {number} period - Period for ATR calculation (default: 14)
     * @returns {Array} ATR values
     */
    static calculateATR(highs, lows, closes, period = 14) {
        try {
            if (!highs || !lows || !closes || 
                highs.length !== lows.length || 
                lows.length !== closes.length || 
                closes.length < period + 1) {
                throw new Error('Invalid data for ATR calculation');
            }

            const trueRanges = [];

            for (let i = 1; i < closes.length; i++) {
                const tr1 = highs[i] - lows[i];
                const tr2 = Math.abs(highs[i] - closes[i - 1]);
                const tr3 = Math.abs(lows[i] - closes[i - 1]);
                
                const trueRange = Math.max(tr1, tr2, tr3);
                trueRanges.push(trueRange);
            }

            // Calculate ATR using EMA
            return this.calculateEMA(trueRanges, period);
        } catch (error) {
            console.error('Error calculating ATR:', error);
            return [];
        }
    }

    /**
     * Calculate Williams %R
     * @param {Array} highs - Array of high prices
     * @param {Array} lows - Array of low prices
     * @param {Array} closes - Array of closing prices
     * @param {number} period - Period for calculation (default: 14)
     * @returns {Array} Williams %R values
     */
    static calculateWilliamsR(highs, lows, closes, period = 14) {
        try {
            if (!highs || !lows || !closes || 
                highs.length !== lows.length || 
                lows.length !== closes.length || 
                closes.length < period) {
                throw new Error('Invalid data for Williams %R calculation');
            }

            const williamsRValues = [];

            for (let i = period - 1; i < closes.length; i++) {
                const highestHigh = Math.max(...highs.slice(i - period + 1, i + 1));
                const lowestLow = Math.min(...lows.slice(i - period + 1, i + 1));
                const currentClose = closes[i];

                const williamsR = ((highestHigh - currentClose) / (highestHigh - lowestLow)) * -100;
                williamsRValues.push(Math.round(williamsR * 100) / 100);
            }

            return williamsRValues;
        } catch (error) {
            console.error('Error calculating Williams %R:', error);
            return [];
        }
    }

    /**
     * Get trading signal based on technical indicators
     * @param {Object} indicators - Object containing various technical indicators
     * @returns {Object} Trading signal with strength and reasoning
     */
    static getTradingSignal(indicators) {
        try {
            const signals = [];
            let bullishCount = 0;
            let bearishCount = 0;

            // RSI analysis
            if (indicators.rsi && indicators.rsi.length > 0) {
                const latestRSI = indicators.rsi[indicators.rsi.length - 1];
                if (latestRSI < 30) {
                    signals.push('RSI oversold - potential buy signal');
                    bullishCount++;
                } else if (latestRSI > 70) {
                    signals.push('RSI overbought - potential sell signal');
                    bearishCount++;
                }
            }

            // MACD analysis
            if (indicators.macd && indicators.macd.macd.length > 1 && indicators.macd.signal.length > 1) {
                const latestMACD = indicators.macd.macd[indicators.macd.macd.length - 1];
                const latestSignal = indicators.macd.signal[indicators.macd.signal.length - 1];
                const prevMACD = indicators.macd.macd[indicators.macd.macd.length - 2];
                const prevSignal = indicators.macd.signal[indicators.macd.signal.length - 2];

                // MACD crossover
                if (prevMACD <= prevSignal && latestMACD > latestSignal) {
                    signals.push('MACD bullish crossover');
                    bullishCount++;
                } else if (prevMACD >= prevSignal && latestMACD < latestSignal) {
                    signals.push('MACD bearish crossover');
                    bearishCount++;
                }
            }

            // Bollinger Bands analysis
            if (indicators.bollinger && indicators.bollinger.upper.length > 0 && indicators.currentPrice) {
                const latestUpper = indicators.bollinger.upper[indicators.bollinger.upper.length - 1];
                const latestLower = indicators.bollinger.lower[indicators.bollinger.lower.length - 1];
                const currentPrice = indicators.currentPrice;

                if (currentPrice <= latestLower) {
                    signals.push('Price at lower Bollinger Band - potential buy');
                    bullishCount++;
                } else if (currentPrice >= latestUpper) {
                    signals.push('Price at upper Bollinger Band - potential sell');
                    bearishCount++;
                }
            }

            // Determine overall signal
            let signal = 'NEUTRAL';
            let strength = 0;

            if (bullishCount > bearishCount) {
                signal = 'BUY';
                strength = Math.min((bullishCount / (bullishCount + bearishCount)) * 100, 100);
            } else if (bearishCount > bullishCount) {
                signal = 'SELL';
                strength = Math.min((bearishCount / (bullishCount + bearishCount)) * 100, 100);
            }

            return {
                signal,
                strength: Math.round(strength),
                reasoning: signals,
                bullishIndicators: bullishCount,
                bearishIndicators: bearishCount
            };
        } catch (error) {
            console.error('Error getting trading signal:', error);
            return {
                signal: 'NEUTRAL',
                strength: 0,
                reasoning: ['Error analyzing indicators'],
                bullishIndicators: 0,
                bearishIndicators: 0
            };
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TechnicalIndicators;
} else {
    window.TechnicalIndicators = TechnicalIndicators;
}