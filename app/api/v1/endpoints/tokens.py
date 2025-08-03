"""
File: app/api/v1/endpoints/tokens.py

API endpoints for token discovery, analysis, and management.
Provides endpoints for new token detection, risk assessment, and liquidity analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_database_session,
    get_multi_chain_manager,
    rate_limiter,
    get_pagination_params,
    optional_auth
)
from app.core.blockchain.multi_chain_manager import MultiChainManager
from app.schemas.token import (
    TokenResponse,
    TokenDiscoveryResponse,
    TokenRiskResponse,
    LiquidityResponse,
    NewTokenScanRequest
)
from app.core.discovery.token_scanner import TokenScanner
from app.core.risk.risk_calculator import RiskCalculator
from app.utils.exceptions import TokenNotFoundError, ChainNotSupportedException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/discover", response_model=TokenDiscoveryResponse)
async def discover_new_tokens(
    networks: Optional[List[str]] = Query(default=None, description="Networks to scan"),
    block_offset: int = Query(default=10, description="Blocks back to scan from latest"),
    min_liquidity: float = Query(default=1000.0, description="Minimum liquidity in USD"),
    multi_chain_manager: MultiChainManager = Depends(get_multi_chain_manager),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    _: None = Depends(rate_limiter),
    api_key: Optional[str] = Depends(optional_auth)
):
    """
    Discover new tokens across specified networks.
    
    Scans recent blocks for newly deployed tokens and filters them
    based on specified criteria like minimum liquidity.
    """
    try:
        # Use enabled networks if none specified
        if networks is None:
            networks = list(await multi_chain_manager.get_enabled_networks())
        
        # Validate networks
        available_networks = await multi_chain_manager.get_enabled_networks()
        invalid_networks = set(networks) - available_networks
        if invalid_networks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid networks: {list(invalid_networks)}"
            )
        
        logger.info(f"Scanning networks {networks} for new tokens")
        
        # Scan for new tokens
        all_new_tokens = await multi_chain_manager.scan_all_chains_for_new_tokens(
            from_block_offset=block_offset
        )
        
        # Filter and format results
        filtered_tokens = []
        total_found = 0
        
        for network, tokens in all_new_tokens.items():
            if network in networks:
                for token in tokens:
                    total_found += 1
                    
                    # Get liquidity information
                    chain = await multi_chain_manager.get_chain(network)
                    if chain:
                        liquidity_info = await chain.get_token_liquidity(token.address)
                        total_liquidity = sum(
                            float(li.total_liquidity_usd) for li in liquidity_info
                        ) if liquidity_info else 0
                        
                        # Apply liquidity filter
                        if total_liquidity >= min_liquidity:
                            token_data = {
                                "address": token.address,
                                "name": token.name,
                                "symbol": token.symbol,
                                "decimals": token.decimals,
                                "network": network,
                                "total_supply": token.total_supply,
                                "verified": token.verified,
                                "created_at": token.created_at,
                                "creator": token.creator,
                                "total_liquidity_usd": total_liquidity,
                                "liquidity_sources": len(liquidity_info) if liquidity_info else 0
                            }
                            filtered_tokens.append(token_data)
        
        # Apply pagination
        start_idx = pagination["skip"]
        end_idx = start_idx + pagination["limit"]
        paginated_tokens = filtered_tokens[start_idx:end_idx]
        
        return TokenDiscoveryResponse(
            tokens=paginated_tokens,
            total_found=total_found,
            total_filtered=len(filtered_tokens),
            networks_scanned=networks,
            block_offset=block_offset,
            min_liquidity_filter=min_liquidity,
            pagination={
                "skip": pagination["skip"],
                "limit": pagination["limit"],
                "total": len(filtered_tokens)
            }
        )
        
    except Exception as e:
        logger.error(f"Token discovery failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Token discovery failed: {str(e)}"
        )


@router.get("/{network}/{token_address}", response_model=TokenResponse)
async def get_token_info(
    network: str,
    token_address: str,
    include_liquidity: bool = Query(default=True, description="Include liquidity data"),
    include_risk: bool = Query(default=True, description="Include risk assessment"),
    multi_chain_manager: MultiChainManager = Depends(get_multi_chain_manager),
    _: None = Depends(rate_limiter),
    api_key: Optional[str] = Depends(optional_auth)
):
    """
    Get detailed information about a specific token.
    
    Returns comprehensive token data including basic info, liquidity,
    and risk assessment if requested.
    """
    try:
        # Get chain instance
        chain = await multi_chain_manager.get_chain(network)
        if not chain:
            raise HTTPException(
                status_code=404,
                detail=f"Network {network} not available"
            )
        
        # Get basic token information
        token_info = await chain.get_token_info(token_address)
        if not token_info:
            raise HTTPException(
                status_code=404,
                detail=f"Token {token_address} not found on {network}"
            )
        
        response_data = {
            "address": token_info.address,
            "name": token_info.name,
            "symbol": token_info.symbol,
            "decimals": token_info.decimals,
            "network": network,
            "total_supply": token_info.total_supply,
            "verified": token_info.verified,
            "created_at": token_info.created_at,
            "creator": token_info.creator
        }
        
        # Add liquidity data if requested
        if include_liquidity:
            liquidity_info = await chain.get_token_liquidity(token_address)
            price = await chain.get_token_price(token_address)
            
            response_data["liquidity"] = {
                "total_liquidity_usd": sum(
                    float(li.total_liquidity_usd) for li in liquidity_info
                ) if liquidity_info else 0,
                "price_usd": float(price) if price else None,
                "liquidity_sources": [
                    {
                        "dex": li.dex,
                        "pair_address": li.pair_address,
                        "liquidity_usd": float(li.total_liquidity_usd),
                        "volume_24h_usd": float(li.volume_24h_usd)
                    }
                    for li in liquidity_info
                ] if liquidity_info else []
            }
        
        # Add risk assessment if requested
        if include_risk:
            risk_calculator = RiskCalculator()
            risk_assessment = await risk_calculator.calculate_token_risk(
                token_address, network, chain
            )
            response_data["risk"] = risk_assessment
        
        return TokenResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get token info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get token information: {str(e)}"
        )


@router.get("/{network}/{token_address}/risk", response_model=TokenRiskResponse)
async def get_token_risk_assessment(
    network: str,
    token_address: str,
    detailed: bool = Query(default=False, description="Include detailed risk factors"),
    multi_chain_manager: MultiChainManager = Depends(get_multi_chain_manager),
    _: None = Depends(rate_limiter),
    api_key: Optional[str] = Depends(optional_auth)
):
    """
    Get detailed risk assessment for a token.
    
    Analyzes various risk factors including contract security,
    liquidity risk, and market manipulation indicators.
    """
    try:
        # Get chain instance
        chain = await multi_chain_manager.get_chain(network)
        if not chain:
            raise HTTPException(
                status_code=404,
                detail=f"Network {network} not available"
            )
        
        # Perform risk assessment
        risk_calculator = RiskCalculator()
        risk_assessment = await risk_calculator.calculate_comprehensive_risk(
            token_address, network, chain, include_details=detailed
        )
        
        return TokenRiskResponse(**risk_assessment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Risk assessment failed: {str(e)}"
        )


@router.get("/{network}/{token_address}/liquidity", response_model=LiquidityResponse)
async def get_token_liquidity(
    network: str,
    token_address: str,
    include_historical: bool = Query(default=False, description="Include historical data"),
    multi_chain_manager: MultiChainManager = Depends(get_multi_chain_manager),
    _: None = Depends(rate_limiter),
    api_key: Optional[str] = Depends(optional_auth)
):
    """
    Get comprehensive liquidity analysis for a token.
    
    Returns current liquidity across all DEXs, trading volumes,
    and optionally historical liquidity data.
    """
    try:
        # Get chain instance
        chain = await multi_chain_manager.get_chain(network)
        if not chain:
            raise HTTPException(
                status_code=404,
                detail=f"Network {network} not available"
            )
        
        # Get liquidity information
        liquidity_info = await chain.get_token_liquidity(token_address)
        price = await chain.get_token_price(token_address)
        
        if not liquidity_info:
            raise HTTPException(
                status_code=404,
                detail=f"No liquidity found for token {token_address}"
            )
        
        # Calculate aggregated metrics
        total_liquidity = sum(float(li.total_liquidity_usd) for li in liquidity_info)
        total_volume_24h = sum(float(li.volume_24h_usd) for li in liquidity_info)
        
        response_data = {
            "token_address": token_address,
            "network": network,
            "current_price_usd": float(price) if price else None,
            "total_liquidity_usd": total_liquidity,
            "total_volume_24h_usd": total_volume_24h,
            "liquidity_sources": [
                {
                    "dex": li.dex,
                    "pair_address": li.pair_address,
                    "token0": li.token0,
                    "token1": li.token1,
                    "reserve0": float(li.reserve0),
                    "reserve1": float(li.reserve1),
                    "liquidity_usd": float(li.total_liquidity_usd),
                    "volume_24h_usd": float(li.volume_24h_usd),
                    "price_usd": float(li.price_usd)
                }
                for li in liquidity_info
            ],
            "metrics": {
                "liquidity_concentration": _calculate_liquidity_concentration(liquidity_info),
                "volume_liquidity_ratio": total_volume_24h / total_liquidity if total_liquidity > 0 else 0,
                "dex_count": len(liquidity_info),
                "largest_pool_percentage": (
                    max(float(li.total_liquidity_usd) for li in liquidity_info) / total_liquidity * 100
                    if liquidity_info and total_liquidity > 0 else 0
                )
            }
        }
        
        # Add historical data if requested
        if include_historical:
            # This would require additional data sources or database storage
            response_data["historical"] = {
                "note": "Historical data not yet implemented",
                "available_periods": []
            }
        
        return LiquidityResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Liquidity analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Liquidity analysis failed: {str(e)}"
        )


@router.post("/scan")
async def trigger_token_scan(
    scan_request: NewTokenScanRequest,
    background_tasks: BackgroundTasks,
    multi_chain_manager: MultiChainManager = Depends(get_multi_chain_manager),
    _: None = Depends(rate_limiter),
    api_key: str = Depends(optional_auth)  # Require auth for manual scans
):
    """
    Trigger a manual token scan across specified networks.
    
    Initiates background scanning for new tokens and returns
    immediately with a task ID for tracking progress.
    """
    try:
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Authentication required for manual scans"
            )
        
        # Validate networks
        available_networks = await multi_chain_manager.get_enabled_networks()
        invalid_networks = set(scan_request.networks) - available_networks
        if invalid_networks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid networks: {list(invalid_networks)}"
            )
        
        # Generate task ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # Add background task
        background_tasks.add_task(
            _background_token_scan,
            task_id,
            scan_request,
            multi_chain_manager
        )
        
        return {
            "task_id": task_id,
            "status": "initiated",
            "networks": scan_request.networks,
            "block_range": {
                "from_block_offset": scan_request.from_block_offset,
                "to_block_offset": scan_request.to_block_offset
            },
            "message": "Token scan initiated. Use task_id to check progress."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate token scan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate scan: {str(e)}"
        )


# Helper functions

def _calculate_liquidity_concentration(liquidity_info: List) -> float:
    """
    Calculate liquidity concentration (Herfindahl index).
    
    Args:
        liquidity_info: List of liquidity information objects
        
    Returns:
        Concentration index (0-1, where 1 is most concentrated)
    """
    if not liquidity_info:
        return 0
    
    total_liquidity = sum(float(li.total_liquidity_usd) for li in liquidity_info)
    if total_liquidity == 0:
        return 0
    
    concentration = sum(
        (float(li.total_liquidity_usd) / total_liquidity) ** 2
        for li in liquidity_info
    )
    
    return concentration


async def _background_token_scan(
    task_id: str,
    scan_request: NewTokenScanRequest,
    multi_chain_manager: MultiChainManager
):
    """
    Background task for token scanning.
    
    Args:
        task_id: Unique task identifier
        scan_request: Scan request parameters
        multi_chain_manager: Multi-chain manager instance
    """
    try:
        logger.info(f"Starting background token scan {task_id}")
        
        # Perform the scan
        results = await multi_chain_manager.scan_all_chains_for_new_tokens(
            from_block_offset=scan_request.from_block_offset
        )
        
        # Store results (in production, this would go to a database or cache)
        # For now, just log the results
        total_tokens = sum(len(tokens) for tokens in results.values())
        logger.info(f"Background scan {task_id} completed. Found {total_tokens} tokens")
        
    except Exception as e:
        logger.error(f"Background scan {task_id} failed: {e}")