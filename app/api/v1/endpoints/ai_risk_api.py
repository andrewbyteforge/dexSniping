"""
AI Risk Assessment API Endpoints
File: app/api/v1/endpoints/ai_risk_api.py

Advanced AI-powered risk assessment endpoints for intelligent trading decisions.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from app.core.trading.ai_risk_assessor import (
    get_ai_risk_assessor,
    AIRiskAssessor,
    RiskAssessment,
    RiskLevel,
    MarketCondition
)

logger = logging.getLogger(__name__)

# Create router
ai_risk_router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class TokenRiskRequest(BaseModel):
    """Request model for token risk assessment."""
    token_symbol: str = Field(..., description="Token symbol (e.g., 'ETH')")
    token_address: str = Field(..., description="Token contract address")
    amount_usd: float = Field(..., gt=0, description="Trade amount in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token_symbol": "ETH",
                "token_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "amount_usd": 1000.0
            }
        }


class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment."""
    token_symbol: str
    overall_risk: str
    risk_score: float
    market_condition: str
    confidence_level: float
    factors: Dict[str, Any]
    recommendations: List[str]
    max_position_size: float
    stop_loss_percentage: float
    take_profit_percentage: float
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "token_symbol": "ETH",
                "overall_risk": "medium",
                "risk_score": 45.2,
                "market_condition": "bullish",
                "confidence_level": 0.85,
                "factors": {
                    "technical": {"momentum_score": 0.7},
                    "liquidity": {"liquidity_score": 0.8},
                    "fundamental": {"market_cap_score": 0.9}
                },
                "recommendations": [
                    "[OK] Low risk detected - favorable conditions",
                    "[PERF] Bullish trend - favorable for long positions"
                ],
                "max_position_size": 800.0,
                "stop_loss_percentage": 5.5,
                "take_profit_percentage": 12.0,
                "timestamp": "2025-08-05T12:00:00Z"
            }
        }


class PortfolioRiskSummaryResponse(BaseModel):
    """Response model for portfolio risk summary."""
    overall_risk: str
    total_positions: int
    high_risk_positions: int
    diversification_score: float
    max_drawdown_risk: float
    recommended_actions: List[str]
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_risk": "medium",
                "total_positions": 5,
                "high_risk_positions": 1,
                "diversification_score": 0.75,
                "max_drawdown_risk": 15.0,
                "recommended_actions": [
                    "Portfolio appears balanced",
                    "Monitor high-risk positions closely"
                ],
                "timestamp": "2025-08-05T12:00:00Z"
            }
        }


class BatchRiskRequest(BaseModel):
    """Request model for batch risk assessment."""
    tokens: List[TokenRiskRequest] = Field(..., description="List of tokens to assess")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tokens": [
                    {
                        "token_symbol": "ETH",
                        "token_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                        "amount_usd": 1000.0
                    },
                    {
                        "token_symbol": "USDC",
                        "token_address": "0xA0b86a33E6417b3dC3558ccE9eDFFE2C2A1db0C8",
                        "amount_usd": 500.0
                    }
                ]
            }
        }


class BatchRiskResponse(BaseModel):
    """Response model for batch risk assessment."""
    assessments: List[RiskAssessmentResponse]
    summary: Dict[str, Any]
    processing_time_ms: float
    timestamp: str


# ==================== DEPENDENCY INJECTION ====================

async def get_risk_assessor() -> AIRiskAssessor:
    """Get AI risk assessor dependency."""
    try:
        return await get_ai_risk_assessor()
    except Exception as error:
        logger.error(f"Failed to get AI risk assessor: {error}")
        raise HTTPException(
            status_code=500,
            detail="AI risk assessment service unavailable"
        )


# ==================== API ENDPOINTS ====================

@ai_risk_router.post(
    "/assess-token",
    response_model=RiskAssessmentResponse,
    summary="Assess Token Risk",
    description="Perform comprehensive AI-powered risk assessment for a token trade"
)
async def assess_token_risk(
    request: TokenRiskRequest,
    risk_assessor: AIRiskAssessor = Depends(get_risk_assessor)
) -> RiskAssessmentResponse:
    """
    Assess the risk of trading a specific token.
    
    Performs comprehensive analysis including:
    - Technical indicator analysis
    - Market sentiment assessment
    - Liquidity and volume analysis
    - Token fundamental analysis
    """
    try:
        logger.info(
            f"Assessing risk for {request.token_symbol} "
            f"(${request.amount_usd:,.2f})"
        )
        
        # Perform risk assessment
        assessment = await risk_assessor.assess_token_risk(
            token_symbol=request.token_symbol,
            token_address=request.token_address,
            amount_usd=request.amount_usd
        )
        
        # Convert to response model
        response = RiskAssessmentResponse(
            token_symbol=assessment.token_symbol,
            overall_risk=assessment.overall_risk.value,
            risk_score=assessment.risk_score,
            market_condition=assessment.market_condition.value,
            confidence_level=assessment.confidence_level,
            factors=assessment.factors,
            recommendations=assessment.recommendations,
            max_position_size=assessment.max_position_size,
            stop_loss_percentage=assessment.stop_loss_percentage,
            take_profit_percentage=assessment.take_profit_percentage,
            timestamp=assessment.timestamp.isoformat()
        )
        
        logger.info(
            f"Risk assessment completed: {assessment.overall_risk.value} "
            f"(score: {assessment.risk_score:.1f})"
        )
        
        return response
        
    except ValueError as error:
        logger.error(f"Invalid token data: {error}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid token data: {str(error)}"
        )
    except Exception as error:
        logger.error(f"Risk assessment failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Risk assessment failed"
        )


@ai_risk_router.post(
    "/assess-batch",
    response_model=BatchRiskResponse,
    summary="Batch Risk Assessment",
    description="Assess risk for multiple tokens simultaneously"
)
async def assess_batch_risk(
    request: BatchRiskRequest,
    risk_assessor: AIRiskAssessor = Depends(get_risk_assessor)
) -> BatchRiskResponse:
    """
    Perform risk assessment for multiple tokens in a single request.
    
    Useful for portfolio analysis and comparing multiple trading opportunities.
    """
    try:
        if len(request.tokens) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 tokens per batch request"
            )
        
        start_time = datetime.utcnow()
        assessments = []
        
        logger.info(f"Processing batch risk assessment for {len(request.tokens)} tokens")
        
        # Process each token
        for token_request in request.tokens:
            try:
                assessment = await risk_assessor.assess_token_risk(
                    token_symbol=token_request.token_symbol,
                    token_address=token_request.token_address,
                    amount_usd=token_request.amount_usd
                )
                
                response = RiskAssessmentResponse(
                    token_symbol=assessment.token_symbol,
                    overall_risk=assessment.overall_risk.value,
                    risk_score=assessment.risk_score,
                    market_condition=assessment.market_condition.value,
                    confidence_level=assessment.confidence_level,
                    factors=assessment.factors,
                    recommendations=assessment.recommendations,
                    max_position_size=assessment.max_position_size,
                    stop_loss_percentage=assessment.stop_loss_percentage,
                    take_profit_percentage=assessment.take_profit_percentage,
                    timestamp=assessment.timestamp.isoformat()
                )
                
                assessments.append(response)
                
            except Exception as token_error:
                logger.error(
                    f"Failed to assess {token_request.token_symbol}: {token_error}"
                )
                # Continue with other tokens
                continue
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Generate batch summary
        summary = _generate_batch_summary(assessments)
        
        response = BatchRiskResponse(
            assessments=assessments,
            summary=summary,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"Batch assessment completed: {len(assessments)} tokens processed "
            f"in {processing_time:.1f}ms"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Batch risk assessment failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Batch risk assessment failed"
        )


@ai_risk_router.get(
    "/portfolio-summary",
    response_model=PortfolioRiskSummaryResponse,
    summary="Portfolio Risk Summary",
    description="Get comprehensive portfolio risk analysis"
)
async def get_portfolio_risk_summary(
    risk_assessor: AIRiskAssessor = Depends(get_risk_assessor)
) -> PortfolioRiskSummaryResponse:
    """
    Get comprehensive portfolio risk analysis.
    
    Provides overall portfolio risk metrics, diversification analysis,
    and actionable recommendations for risk management.
    """
    try:
        logger.info("Generating portfolio risk summary")
        
        # Get portfolio risk summary
        summary_data = await risk_assessor.get_portfolio_risk_summary()
        
        response = PortfolioRiskSummaryResponse(
            overall_risk=summary_data["overall_risk"],
            total_positions=summary_data.get("total_positions", 0),
            high_risk_positions=summary_data.get("high_risk_positions", 0),
            diversification_score=summary_data.get("diversification_score", 0.0),
            max_drawdown_risk=summary_data.get("max_drawdown_risk", 0.0),
            recommended_actions=summary_data.get("recommended_actions", []),
            timestamp=summary_data.get("timestamp", datetime.utcnow().isoformat())
        )
        
        logger.info("Portfolio risk summary generated successfully")
        return response
        
    except Exception as error:
        logger.error(f"Portfolio risk summary failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Portfolio risk analysis unavailable"
        )


@ai_risk_router.get(
    "/risk-levels",
    summary="Get Risk Levels",
    description="Get available risk levels and their descriptions"
)
async def get_risk_levels() -> Dict[str, Any]:
    """
    Get information about available risk levels.
    
    Returns descriptions and thresholds for each risk level.
    """
    try:
        risk_levels = {
            "levels": {
                RiskLevel.VERY_LOW.value: {
                    "description": "Very low risk - minimal potential for loss",
                    "score_range": "0-15",
                    "recommended_action": "Safe to trade with larger positions"
                },
                RiskLevel.LOW.value: {
                    "description": "Low risk - favorable trading conditions",
                    "score_range": "16-30",
                    "recommended_action": "Good trading opportunity"
                },
                RiskLevel.MEDIUM.value: {
                    "description": "Medium risk - standard market conditions",
                    "score_range": "31-50",
                    "recommended_action": "Trade with normal caution"
                },
                RiskLevel.HIGH.value: {
                    "description": "High risk - increased potential for loss",
                    "score_range": "51-70",
                    "recommended_action": "Use smaller positions and tight stops"
                },
                RiskLevel.VERY_HIGH.value: {
                    "description": "Very high risk - significant loss potential",
                    "score_range": "71-85",
                    "recommended_action": "Avoid or use very small positions"
                },
                RiskLevel.EXTREME.value: {
                    "description": "Extreme risk - high probability of loss",
                    "score_range": "86-100",
                    "recommended_action": "Avoid trading"
                }
            },
            "market_conditions": {
                MarketCondition.BULLISH.value: "Upward price trend with positive momentum",
                MarketCondition.BEARISH.value: "Downward price trend with negative momentum",
                MarketCondition.SIDEWAYS.value: "Stable price with low volatility",
                MarketCondition.VOLATILE.value: "High price volatility and uncertainty",
                MarketCondition.UNCERTAIN.value: "Unclear market direction"
            }
        }
        
        return risk_levels
        
    except Exception as error:
        logger.error(f"Failed to get risk levels: {error}")
        raise HTTPException(
            status_code=500,
            detail="Risk level information unavailable"
        )


@ai_risk_router.get(
    "/health",
    summary="AI Risk System Health",
    description="Check the health status of the AI risk assessment system"
)
async def get_ai_risk_health(
    risk_assessor: AIRiskAssessor = Depends(get_risk_assessor)
) -> Dict[str, Any]:
    """
    Check the health status of the AI risk assessment system.
    
    Returns system status, performance metrics, and operational information.
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "AI Risk Assessment System",
            "version": "1.0.0",
            "features": {
                "token_risk_assessment": True,
                "portfolio_analysis": True,
                "batch_processing": True,
                "real_time_analysis": True
            },
            "cache_info": {
                "cached_assessments": len(risk_assessor.assessment_cache),
                "cache_hit_rate": "N/A"  # Would calculate from metrics
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as error:
        logger.error(f"AI risk health check failed: {error}")
        return {
            "status": "unhealthy",
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }


# ==================== HELPER FUNCTIONS ====================

def _generate_batch_summary(assessments: List[RiskAssessmentResponse]) -> Dict[str, Any]:
    """
    Generate summary statistics for batch assessment results.
    
    Args:
        assessments: List of risk assessment responses
        
    Returns:
        Dict[str, Any]: Batch summary statistics
    """
    if not assessments:
        return {
            "total_tokens": 0,
            "average_risk_score": 0.0,
            "risk_distribution": {},
            "recommendations": ["No tokens assessed"]
        }
    
    # Calculate statistics
    total_tokens = len(assessments)
    risk_scores = [a.risk_score for a in assessments]
    average_risk_score = sum(risk_scores) / len(risk_scores)
    
    # Risk level distribution
    risk_levels = [a.overall_risk for a in assessments]
    risk_distribution = {}
    for level in risk_levels:
        risk_distribution[level] = risk_distribution.get(level, 0) + 1
    
    # Generate batch recommendations
    high_risk_count = sum(1 for a in assessments if a.risk_score > 70)
    recommendations = []
    
    if high_risk_count > 0:
        recommendations.append(f"[WARN] {high_risk_count} high-risk tokens detected")
    
    if average_risk_score < 30:
        recommendations.append("[OK] Overall low risk portfolio")
    elif average_risk_score > 70:
        recommendations.append("[EMOJI] High-risk portfolio - exercise caution")
    else:
        recommendations.append("[STATS] Moderate risk portfolio")
    
    return {
        "total_tokens": total_tokens,
        "average_risk_score": round(average_risk_score, 2),
        "risk_distribution": risk_distribution,
        "high_risk_tokens": high_risk_count,
        "recommendations": recommendations
    }


# Export router
__all__ = ["ai_risk_router"]