"""
File: app/core/risk/risk_calculator.py

Advanced risk assessment calculator for token analysis and security evaluation.
Provides comprehensive risk scoring for discovered tokens.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta
import re
import hashlib

from app.core.blockchain.base_chain import BaseChain, TokenInfo, LiquidityInfo
from app.core.performance.cache_manager import cache_manager
from app.core.performance.circuit_breaker import CircuitBreakerManager
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException
from app.config import settings

logger = setup_logger(__name__)


class RiskCalculatorError(DexSnipingException):
    """Exception raised when risk calculation operations fail."""
    pass


@dataclass
class RiskFactors:
    """Individual risk factors for a token."""
    liquidity_risk: float = 0.0  # 0-10 scale
    contract_risk: float = 0.0   # 0-10 scale
    market_risk: float = 0.0     # 0-10 scale
    social_risk: float = 0.0     # 0-10 scale
    technical_risk: float = 0.0  # 0-10 scale
    
    @property
    def overall_risk(self) -> float:
        """Calculate weighted overall risk score."""
        weights = {
            'liquidity_risk': 0.25,
            'contract_risk': 0.30,
            'market_risk': 0.20,
            'social_risk': 0.15,
            'technical_risk': 0.10
        }
        
        total_score = (
            self.liquidity_risk * weights['liquidity_risk'] +
            self.contract_risk * weights['contract_risk'] +
            self.market_risk * weights['market_risk'] +
            self.social_risk * weights['social_risk'] +
            self.technical_risk * weights['technical_risk']
        )
        
        return min(10.0, max(0.0, total_score))


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment for a token."""
    token_address: str
    network: str
    risk_factors: RiskFactors
    risk_score: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    confidence: float  # 0-1 scale
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_risk_score(
        cls,
        token_address: str,
        network: str,
        risk_factors: RiskFactors,
        confidence: float = 1.0,
        warnings: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'RiskAssessment':
        """Create RiskAssessment from risk factors."""
        risk_score = risk_factors.overall_risk
        
        # Determine risk level
        if risk_score >= 8.0:
            risk_level = "CRITICAL"
        elif risk_score >= 6.0:
            risk_level = "HIGH"
        elif risk_score >= 4.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return cls(
            token_address=token_address,
            network=network,
            risk_factors=risk_factors,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            warnings=warnings or [],
            recommendations=recommendations or [],
            metadata=metadata or {}
        )


class RiskCalculator:
    """
    Advanced risk assessment calculator for token security analysis.
    
    Features:
    - Multi-factor risk analysis
    - Liquidity concentration analysis
    - Contract security assessment
    - Market manipulation detection
    - Social sentiment analysis
    - Technical pattern recognition
    """
    
    def __init__(self):
        """Initialize risk calculator."""
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.cache_ttl = getattr(settings, 'risk_cache_ttl', 3600)  # 1 hour default
        
        # Risk thresholds configuration
        self.thresholds = {
            'min_liquidity_usd': getattr(settings, 'min_liquidity_usd_int', 10000),
            'max_liquidity_concentration': 0.8,  # 80% in single pool
            'min_holders': 100,
            'max_total_supply': 10**15,  # 1 quadrillion max
            'min_trading_volume_24h': 1000,
            'honeypot_risk_threshold': 7.0
        }
    
    async def calculate_token_risk(
        self,
        token_address: str,
        network: str,
        chain: BaseChain,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk assessment for a token.
        
        Args:
            token_address: Token contract address
            network: Network name
            chain: Blockchain chain instance
            include_details: Include detailed risk factor breakdown
            
        Returns:
            Risk assessment dictionary
        """
        try:
            # Check cache first
            cache_key = f"risk_{network}_{token_address}"
            cached_result = await cache_manager.get(cache_key, namespace="risk")
            
            if cached_result and not include_details:
                logger.debug(f"Using cached risk assessment for {token_address}")
                return cached_result
            
            # Get circuit breaker for risk calculations
            breaker = self.circuit_breaker_manager.get_breaker(f"risk_calc_{network}")
            
            # Calculate risk with protection
            assessment = await breaker.call(
                self._perform_risk_calculation,
                token_address,
                network,
                chain,
                include_details
            )
            
            # Convert to dict for API response
            result = {
                "token_address": assessment.token_address,
                "network": assessment.network,
                "risk_score": round(assessment.risk_score, 2),
                "risk_level": assessment.risk_level,
                "confidence": round(assessment.confidence, 2),
                "warnings": assessment.warnings,
                "recommendations": assessment.recommendations,
                "assessment_timestamp": assessment.assessment_timestamp.isoformat()
            }
            
            if include_details:
                result["risk_factors"] = {
                    "liquidity_risk": round(assessment.risk_factors.liquidity_risk, 2),
                    "contract_risk": round(assessment.risk_factors.contract_risk, 2),
                    "market_risk": round(assessment.risk_factors.market_risk, 2),
                    "social_risk": round(assessment.risk_factors.social_risk, 2),
                    "technical_risk": round(assessment.risk_factors.technical_risk, 2)
                }
                result["metadata"] = assessment.metadata
            
            # Cache result
            await cache_manager.set(
                cache_key,
                result,
                ttl=self.cache_ttl,
                namespace="risk"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Risk calculation failed for {token_address}: {e}")
            # Return high-risk assessment on error
            return {
                "token_address": token_address,
                "network": network,
                "risk_score": 9.0,
                "risk_level": "CRITICAL",
                "confidence": 0.5,
                "warnings": [f"Risk calculation failed: {str(e)}"],
                "recommendations": ["Avoid trading due to assessment failure"],
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
    
    async def calculate_comprehensive_risk(
        self,
        token_address: str,
        network: str,
        chain: BaseChain,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk assessment with full details.
        
        Args:
            token_address: Token contract address
            network: Network name
            chain: Blockchain chain instance
            include_details: Include detailed analysis
            
        Returns:
            Comprehensive risk assessment
        """
        return await self.calculate_token_risk(
            token_address, network, chain, include_details=True
        )
    
    async def _perform_risk_calculation(
        self,
        token_address: str,
        network: str,
        chain: BaseChain,
        include_details: bool
    ) -> RiskAssessment:
        """
        Perform the actual risk calculation.
        
        Args:
            token_address: Token contract address
            network: Network name
            chain: Blockchain chain instance
            include_details: Include detailed analysis
            
        Returns:
            RiskAssessment object
        """
        logger.info(f"Calculating risk for token {token_address} on {network}")
        
        # Get token information
        token_info = await chain.get_token_info(token_address)
        if not token_info:
            raise RiskCalculatorError(f"Could not get token info for {token_address}")
        
        # Initialize risk factors
        risk_factors = RiskFactors()
        warnings = []
        recommendations = []
        metadata = {}
        confidence = 1.0
        
        # Calculate individual risk factors
        try:
            # 1. Liquidity Risk Analysis
            liquidity_risk, liquidity_warnings, liquidity_meta = await self._analyze_liquidity_risk(
                token_address, chain
            )
            risk_factors.liquidity_risk = liquidity_risk
            warnings.extend(liquidity_warnings)
            metadata.update(liquidity_meta)
            
        except Exception as e:
            logger.warning(f"Liquidity risk analysis failed: {e}")
            risk_factors.liquidity_risk = 8.0  # High risk on failure
            warnings.append("Liquidity analysis failed")
            confidence *= 0.8
        
        try:
            # 2. Contract Security Risk
            contract_risk, contract_warnings, contract_meta = await self._analyze_contract_risk(
                token_address, token_info, chain
            )
            risk_factors.contract_risk = contract_risk
            warnings.extend(contract_warnings)
            metadata.update(contract_meta)
            
        except Exception as e:
            logger.warning(f"Contract risk analysis failed: {e}")
            risk_factors.contract_risk = 7.0  # High risk on failure
            warnings.append("Contract analysis failed")
            confidence *= 0.8
        
        try:
            # 3. Market Risk Analysis
            market_risk, market_warnings, market_meta = await self._analyze_market_risk(
                token_info
            )
            risk_factors.market_risk = market_risk
            warnings.extend(market_warnings)
            metadata.update(market_meta)
            
        except Exception as e:
            logger.warning(f"Market risk analysis failed: {e}")
            risk_factors.market_risk = 6.0  # Medium-high risk on failure
            confidence *= 0.9
        
        # 4. Social Risk Analysis (simplified)
        risk_factors.social_risk = await self._analyze_social_risk(token_info)
        
        # 5. Technical Risk Analysis
        risk_factors.technical_risk = await self._analyze_technical_risk(token_info)
        
        # Generate recommendations based on risk factors
        recommendations = self._generate_recommendations(risk_factors, warnings)
        
        # Create assessment
        assessment = RiskAssessment.from_risk_score(
            token_address=token_address,
            network=network,
            risk_factors=risk_factors,
            confidence=confidence,
            warnings=warnings,
            recommendations=recommendations,
            metadata=metadata
        )
        
        logger.info(
            f"Risk assessment completed for {token_address}: "
            f"{assessment.risk_score:.2f} ({assessment.risk_level})"
        )
        
        return assessment
    
    async def _analyze_liquidity_risk(
        self,
        token_address: str,
        chain: BaseChain
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """
        Analyze liquidity-related risks.
        
        Returns:
            Tuple of (risk_score, warnings, metadata)
        """
        warnings = []
        metadata = {}
        risk_score = 5.0  # Default medium risk
        
        try:
            # Get liquidity information
            liquidity_info = await chain.get_token_liquidity(token_address)
            
            if not liquidity_info:
                warnings.append("No liquidity pools found")
                return 9.0, warnings, {"total_liquidity_usd": 0}
            
            # Calculate total liquidity
            total_liquidity = sum(float(li.total_liquidity_usd) for li in liquidity_info)
            metadata["total_liquidity_usd"] = total_liquidity
            metadata["liquidity_pools"] = len(liquidity_info)
            
            # Risk based on total liquidity
            if total_liquidity < 1000:
                risk_score = 9.0
                warnings.append("Very low liquidity (<$1K)")
            elif total_liquidity < 10000:
                risk_score = 7.0
                warnings.append("Low liquidity (<$10K)")
            elif total_liquidity < 50000:
                risk_score = 5.0
                warnings.append("Medium liquidity (<$50K)")
            elif total_liquidity < 100000:
                risk_score = 3.0
            else:
                risk_score = 1.0
            
            # Analyze liquidity concentration
            if len(liquidity_info) > 1:
                largest_pool = max(liquidity_info, key=lambda x: x.total_liquidity_usd)
                concentration = float(largest_pool.total_liquidity_usd) / total_liquidity
                
                metadata["liquidity_concentration"] = concentration
                
                if concentration > 0.9:
                    risk_score = min(risk_score + 2.0, 10.0)
                    warnings.append("High liquidity concentration (>90% in one pool)")
                elif concentration > 0.8:
                    risk_score = min(risk_score + 1.0, 10.0)
                    warnings.append("Medium liquidity concentration (>80% in one pool)")
            
            return risk_score, warnings, metadata
            
        except Exception as e:
            logger.error(f"Liquidity risk analysis failed: {e}")
            return 8.0, ["Liquidity analysis failed"], {}
    
    async def _analyze_contract_risk(
        self,
        token_address: str,
        token_info: TokenInfo,
        chain: BaseChain
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """
        Analyze contract security risks.
        
        Returns:
            Tuple of (risk_score, warnings, metadata)
        """
        warnings = []
        metadata = {}
        risk_score = 5.0  # Default medium risk
        
        try:
            # Get contract security info
            security_info = await chain.check_contract_security(token_address)
            metadata["contract_security"] = security_info
            
            # Check if contract is verified
            if not token_info.verified:
                risk_score += 2.0
                warnings.append("Contract source code not verified")
            
            # Check for basic security issues
            if not security_info.get("is_safe", True):
                risk_score += 3.0
                warnings.append("Contract security concerns detected")
            
            # Check contract age (if available)
            if token_info.created_at:
                # Recent contracts are riskier
                hours_old = (datetime.utcnow().timestamp() - token_info.created_at) / 3600
                metadata["contract_age_hours"] = hours_old
                
                if hours_old < 1:
                    risk_score += 2.0
                    warnings.append("Very new contract (<1 hour old)")
                elif hours_old < 24:
                    risk_score += 1.0
                    warnings.append("New contract (<24 hours old)")
            
            return min(risk_score, 10.0), warnings, metadata
            
        except Exception as e:
            logger.error(f"Contract risk analysis failed: {e}")
            return 7.0, ["Contract analysis failed"], {}
    
    async def _analyze_market_risk(
        self,
        token_info: TokenInfo
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """
        Analyze market-related risks.
        
        Returns:
            Tuple of (risk_score, warnings, metadata)
        """
        warnings = []
        metadata = {}
        risk_score = 5.0  # Default medium risk
        
        # Check total supply
        if token_info.total_supply:
            metadata["total_supply"] = token_info.total_supply
            
            # Very high supply can indicate inflation risk
            if token_info.total_supply > 10**15:  # 1 quadrillion
                risk_score += 2.0
                warnings.append("Extremely high total supply")
            elif token_info.total_supply > 10**12:  # 1 trillion
                risk_score += 1.0
                warnings.append("Very high total supply")
        
        # Check token name and symbol for suspicious patterns
        suspicious_patterns = [
            r'test',
            r'fake',
            r'scam',
            r'pump',
            r'moon',
            r'safe',
            r'baby',
            r'mini',
            r'doge.*coin',
            r'shib.*inu'
        ]
        
        token_text = f"{token_info.name} {token_info.symbol}".lower()
        
        for pattern in suspicious_patterns:
            if re.search(pattern, token_text):
                risk_score += 0.5
                warnings.append(f"Suspicious name pattern detected: {pattern}")
        
        # Check for very short or very long names
        if len(token_info.symbol) < 2:
            risk_score += 1.0
            warnings.append("Very short symbol")
        elif len(token_info.symbol) > 10:
            risk_score += 0.5
            warnings.append("Very long symbol")
        
        if len(token_info.name) < 3:
            risk_score += 1.0
            warnings.append("Very short name")
        elif len(token_info.name) > 50:
            risk_score += 0.5
            warnings.append("Very long name")
        
        return min(risk_score, 10.0), warnings, metadata
    
    async def _analyze_social_risk(self, token_info: TokenInfo) -> float:
        """
        Analyze social sentiment risks (simplified implementation).
        
        Args:
            token_info: Token information
            
        Returns:
            Social risk score (0-10)
        """
        # Simplified social risk analysis
        # In a full implementation, this would check:
        # - Social media sentiment
        # - Community size and engagement
        # - Developer activity
        # - News sentiment
        
        risk_score = 5.0  # Default neutral
        
        # Check for meme coin indicators
        meme_indicators = ['doge', 'shib', 'pepe', 'wojak', 'chad', 'moon']
        token_text = f"{token_info.name} {token_info.symbol}".lower()
        
        for indicator in meme_indicators:
            if indicator in token_text:
                risk_score += 1.0  # Meme coins are riskier
                break
        
        return min(risk_score, 10.0)
    
    async def _analyze_technical_risk(self, token_info: TokenInfo) -> float:
        """
        Analyze technical risks.
        
        Args:
            token_info: Token information
            
        Returns:
            Technical risk score (0-10)
        """
        risk_score = 2.0  # Default low technical risk
        
        # Check decimals
        if token_info.decimals > 18:
            risk_score += 2.0  # Unusual decimal count
        elif token_info.decimals == 0:
            risk_score += 1.0  # No decimals might be unusual
        
        # Check for standard ERC-20 compliance
        if not all([token_info.name, token_info.symbol, token_info.decimals is not None]):
            risk_score += 3.0  # Missing standard fields
        
        return min(risk_score, 10.0)
    
    def _generate_recommendations(
        self,
        risk_factors: RiskFactors,
        warnings: List[str]
    ) -> List[str]:
        """
        Generate trading recommendations based on risk assessment.
        
        Args:
            risk_factors: Calculated risk factors
            warnings: List of warnings
            
        Returns:
            List of recommendations
        """
        recommendations = []
        overall_risk = risk_factors.overall_risk
        
        if overall_risk >= 8.0:
            recommendations.extend([
                "AVOID: Critical risk level detected",
                "Do not trade this token",
                "High probability of loss"
            ])
        elif overall_risk >= 6.0:
            recommendations.extend([
                "CAUTION: High risk level",
                "Only trade with extreme caution",
                "Use very small position sizes",
                "Set tight stop losses"
            ])
        elif overall_risk >= 4.0:
            recommendations.extend([
                "MODERATE: Medium risk level",
                "Trade with caution",
                "Use appropriate position sizing",
                "Monitor closely"
            ])
        else:
            recommendations.extend([
                "ACCEPTABLE: Low risk level",
                "Trade with normal position sizing",
                "Monitor for changes"
            ])
        
        # Specific recommendations based on risk factors
        if risk_factors.liquidity_risk >= 7.0:
            recommendations.append("Low liquidity: Expect high slippage")
        
        if risk_factors.contract_risk >= 7.0:
            recommendations.append("Contract risks: Verify code before trading")
        
        if risk_factors.market_risk >= 7.0:
            recommendations.append("Market risks: High volatility expected")
        
        return recommendations
    
    async def get_risk_stats(self) -> Dict[str, Any]:
        """
        Get risk calculator statistics.
        
        Returns:
            Statistics dictionary
        """
        cache_stats = await cache_manager.get_stats()
        breaker_stats = await self.circuit_breaker_manager.get_all_stats()
        
        risk_breakers = {
            name: stats for name, stats in breaker_stats.items()
            if name.startswith('risk_calc_')
        }
        
        return {
            "cache_performance": {
                "cache_type": cache_stats.get("cache_type", "unknown"),
                "hit_rate": cache_stats.get("hit_rate", 0)
            },
            "circuit_breakers": risk_breakers,
            "configuration": {
                "cache_ttl_seconds": self.cache_ttl,
                "thresholds": self.thresholds
            }
        }