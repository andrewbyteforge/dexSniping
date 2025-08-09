"""
Wallet API Endpoints - Phase 4B
File: app/api/v1/endpoints/wallet.py

Professional wallet management API endpoints that integrate with the enhanced
wallet system and provide comprehensive wallet functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.utils.logger import setup_logger, get_performance_logger, get_performance_logger
from app.core.wallet.enhanced_wallet_manager import (
    get_enhanced_wallet_manager,
    EnhancedWalletManager,
    WalletType,
    ConnectionStatus
)
from app.core.blockchain.network_manager_fixed import NetworkType
from app.core.exceptions import WalletError, NetworkError

logger = setup_logger(__name__, "api")

# Create router
router = APIRouter(prefix="/wallet", tags=["wallet"])


# ==================== REQUEST/RESPONSE MODELS ====================

class WalletConnectionRequest(BaseModel):
    """Request model for wallet connection."""
    wallet_type: WalletType = Field(..., description="Type of wallet to connect")
    network_type: NetworkType = Field(..., description="Blockchain network to connect to")
    address: Optional[str] = Field(None, description="Optional wallet address if known")


class WalletConnectionResponse(BaseModel):
    """Response model for wallet connection."""
    success: bool
    connection_id: Optional[str] = None
    wallet_info: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


class NetworkSwitchRequest(BaseModel):
    """Request model for network switching."""
    connection_id: str = Field(..., description="Connection ID to switch")
    new_network: NetworkType = Field(..., description="New network to switch to")


class WalletBalanceResponse(BaseModel):
    """Response model for wallet balance."""
    success: bool
    balance: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TransactionHistoryResponse(BaseModel):
    """Response model for transaction history."""
    success: bool
    transactions: Optional[List[Dict[str, Any]]] = None
    total_count: Optional[int] = None
    error: Optional[str] = None


# ==================== DEPENDENCY INJECTION ====================

def get_wallet_manager() -> EnhancedWalletManager:
    """Dependency to get wallet manager instance."""
    try:
        return get_enhanced_wallet_manager()
    except Exception as e:
        logger.error(f"❌ Failed to get wallet manager: {e}")
        raise HTTPException(status_code=500, detail="Wallet manager unavailable")


# ==================== WALLET CONNECTION ENDPOINTS ====================

@router.post("/connect", response_model=WalletConnectionResponse)
async def connect_wallet(
    request: WalletConnectionRequest,
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> WalletConnectionResponse:
    """
    Connect a wallet to the specified network.
    
    This endpoint initiates a wallet connection process and returns connection details.
    """
    try:
        logger.info(f"🔗 API: Connecting {request.wallet_type.value} to {request.network_type.value}")
        
        result = await wallet_manager.connect_wallet(
            wallet_type=request.wallet_type,
            network_type=request.network_type,
            address=request.address
        )
        
        if result["success"]:
            logger.info(f"✅ API: Wallet connected successfully - ID: {result['connection_id']}")
            
            return WalletConnectionResponse(
                success=True,
                connection_id=result["connection_id"],
                wallet_info={
                    "wallet_type": result["wallet_info"].wallet_type.value,
                    "address": result["wallet_info"].address,
                    "network": result["wallet_info"].network_type.value,
                    "chain_id": result["wallet_info"].chain_id,
                    "connected_at": result["wallet_info"].connected_at.isoformat(),
                    "session_id": result["wallet_info"].session_id
                },
                message=result["message"]
            )
        else:
            logger.warning(f"⚠️ API: Wallet connection failed - {result['error']}")
            
            return WalletConnectionResponse(
                success=False,
                error=result["error"]
            )
            
    except Exception as e:
        error_msg = f"Wallet connection API error: {e}"
        logger.error(f"❌ {error_msg}")
        
        return WalletConnectionResponse(
            success=False,
            error=error_msg
        )


@router.delete("/disconnect/{connection_id}")
async def disconnect_wallet(
    connection_id: str,
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """
    Disconnect a wallet connection.
    
    Args:
        connection_id: The connection ID to disconnect
    """
    try:
        logger.info(f"🔌 API: Disconnecting wallet - ID: {connection_id}")
        
        result = await wallet_manager.disconnect_wallet(connection_id)
        
        if result["success"]:
            logger.info(f"✅ API: Wallet disconnected successfully")
            return {
                "success": True,
                "message": result["message"],
                "connection_id": connection_id
            }
        else:
            logger.warning(f"⚠️ API: Wallet disconnection failed - {result['error']}")
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Wallet disconnection API error: {e}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


# ==================== WALLET INFORMATION ENDPOINTS ====================

@router.get("/connections")
async def get_active_connections(
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """
    Get information about all active wallet connections.
    """
    try:
        logger.info("📋 API: Getting active wallet connections")
        
        connections = wallet_manager.get_active_connections()
        
        return {
            "success": True,
            "active_connections": connections,
            "total_connections": len(connections),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Get connections API error: {e}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/supported")
async def get_supported_wallets(
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """
    Get information about supported wallet types and their capabilities.
    """
    try:
        logger.info("📋 API: Getting supported wallets")
        
        supported_wallets = wallet_manager.get_supported_wallets()
        
        return {
            "success": True,
            "supported_wallets": supported_wallets,
            "total_wallet_types": len(supported_wallets)
        }
        
    except Exception as e:
        error_msg = f"Get supported wallets API error: {e}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


# ==================== WALLET BALANCE ENDPOINTS ====================

@router.get("/balance/{connection_id}", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    connection_id: str,
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> WalletBalanceResponse:
    """
    Get balance information for a connected wallet.
    
    Args:
        connection_id: The connection ID to get balance for
    """
    try:
        logger.info(f"💰 API: Getting wallet balance - ID: {connection_id}")
        
        result = await wallet_manager.get_wallet_balance(connection_id)
        
        if result["success"]:
            logger.info(f"✅ API: Balance retrieved successfully")
            
            return WalletBalanceResponse(
                success=True,
                balance=result["balance"]
            )
        else:
            logger.warning(f"⚠️ API: Balance retrieval failed - {result['error']}")
            
            return WalletBalanceResponse(
                success=False,
                error=result["error"]
            )
            
    except Exception as e:
        error_msg = f"Get balance API error: {e}"
        logger.error(f"❌ {error_msg}")
        
        return WalletBalanceResponse(
            success=False,
            error=error_msg
        )


@router.post("/balance/{connection_id}/refresh", response_model=WalletBalanceResponse)
async def refresh_wallet_balance(
    connection_id: str,
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> WalletBalanceResponse:
    """
    Manually refresh wallet balance from blockchain.
    
    Args:
        connection_id: The connection ID to refresh balance for
    """
    try:
        logger.info(f"🔄 API: Refreshing wallet balance - ID: {connection_id}")
        
        result = await wallet_manager.refresh_wallet_balance(connection_id)
        
        if result["success"]:
            logger.info(f"✅ API: Balance refreshed successfully")
            
            return WalletBalanceResponse(
                success=True,
                balance=result["balance"]
            )
        else:
            logger.warning(f"⚠️ API: Balance refresh failed - {result['error']}")
            
            return WalletBalanceResponse(
                success=False,
                error=result["error"]
            )
            
    except Exception as e:
        error_msg = f"Refresh balance API error: {e}"
        logger.error(f"❌ {error_msg}")
        
        return WalletBalanceResponse(
            success=False,
            error=error_msg
        )


# ==================== NETWORK MANAGEMENT ENDPOINTS ====================

@router.post("/switch-network")
async def switch_wallet_network(
    request: NetworkSwitchRequest,
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """
    Switch wallet to a different blockchain network.
    """
    try:
        logger.info(f"🔄 API: Switching network - ID: {request.connection_id}, Network: {request.new_network.value}")
        
        result = await wallet_manager.switch_network(
            connection_id=request.connection_id,
            new_network=request.new_network
        )
        
        if result["success"]:
            logger.info(f"✅ API: Network switched successfully")
            return result
        else:
            logger.warning(f"⚠️ API: Network switch failed - {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Switch network API error: {e}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


# ==================== TRANSACTION ENDPOINTS ====================

@router.get("/transactions/{connection_id}", response_model=TransactionHistoryResponse)
async def get_wallet_transactions(
    connection_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of transactions to retrieve"),
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> TransactionHistoryResponse:
    """
    Get transaction history for a connected wallet.
    
    Args:
        connection_id: The connection ID to get transactions for
        limit: Maximum number of transactions to retrieve
    """
    try:
        logger.info(f"📜 API: Getting transaction history - ID: {connection_id}, Limit: {limit}")
        
        result = await wallet_manager.get_wallet_transaction_history(
            connection_id=connection_id,
            limit=limit
        )
        
        if result["success"]:
            logger.info(f"✅ API: Transaction history retrieved - {result['total_count']} transactions")
            
            return TransactionHistoryResponse(
                success=True,
                transactions=result["transactions"],
                total_count=result["total_count"]
            )
        else:
            logger.warning(f"⚠️ API: Transaction history failed - {result['error']}")
            
            return TransactionHistoryResponse(
                success=False,
                error=result["error"]
            )
            
    except Exception as e:
        error_msg = f"Get transactions API error: {e}"
        logger.error(f"❌ {error_msg}")
        
        return TransactionHistoryResponse(
            success=False,
            error=error_msg
        )


# ==================== HEALTH AND STATUS ENDPOINTS ====================

@router.get("/health")
async def wallet_system_health(
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """
    Get wallet system health and status information.
    """
    try:
        logger.info("❤️ API: Checking wallet system health")
        
        connections = wallet_manager.get_active_connections()
        supported_wallets = wallet_manager.get_supported_wallets()
        
        health_status = {
            "status": "healthy",
            "system": "Enhanced Wallet Manager",
            "version": "4.0.0-beta",
            "active_connections": len(connections),
            "max_connections": wallet_manager.max_concurrent_connections,
            "supported_wallet_types": len(supported_wallets),
            "supported_networks": list(set([
                network for wallet_config in supported_wallets.values()
                for network in wallet_config["supported_networks"]
            ])),
            "connection_timeout_minutes": wallet_manager.connection_timeout_minutes,
            "balance_refresh_interval_seconds": wallet_manager.balance_refresh_interval,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("✅ API: Wallet system health check complete")
        
        return health_status
        
    except Exception as e:
        error_msg = f"Wallet health check API error: {e}"
        logger.error(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "system": "Enhanced Wallet Manager",
            "error": error_msg,
            "timestamp": datetime.utcnow().isoformat()
        }


# ==================== CLEANUP ENDPOINTS ====================

@router.post("/cleanup/expired")
async def cleanup_expired_connections(
    wallet_manager: EnhancedWalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """
    Manually trigger cleanup of expired wallet connections.
    """
    try:
        logger.info("🧹 API: Manual cleanup of expired connections")
        
        # Get count before cleanup
        connections_before = len(wallet_manager.get_active_connections())
        
        # Perform cleanup
        await wallet_manager._cleanup_expired_connections()
        
        # Get count after cleanup
        connections_after = len(wallet_manager.get_active_connections())
        cleaned_count = connections_before - connections_after
        
        logger.info(f"✅ API: Cleanup complete - removed {cleaned_count} expired connections")
        
        return {
            "success": True,
            "connections_before": connections_before,
            "connections_after": connections_after,
            "cleaned_count": cleaned_count,
            "message": f"Cleaned up {cleaned_count} expired connections"
        }
        
    except Exception as e:
        error_msg = f"Cleanup API error: {e}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


# Export the router
__all__ = ["router"]