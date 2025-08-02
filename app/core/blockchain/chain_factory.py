"""
File: app/core/blockchain/chain_factory.py

Factory class for creating blockchain chain instances.
Manages the creation and configuration of different chain types.
"""

from typing import Dict, Type, Optional
from app.core.blockchain.base_chain import BaseChain, ChainType
from app.config import NetworkConfig, settings
from app.utils.exceptions import ChainNotSupportedException, ChainConnectionException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChainFactory:
    """
    Factory class for creating blockchain chain instances.
    
    This factory manages the creation of different chain implementations
    based on network configuration and provides a unified interface
    for chain creation across the application.
    """
    
    _chain_classes: Dict[ChainType, Type[BaseChain]] = {}
    _instances: Dict[str, BaseChain] = {}
    
    @classmethod
    def register_chain_class(cls, chain_type: ChainType, chain_class: Type[BaseChain]):
        """
        Register a chain implementation class.
        
        Args:
            chain_type: Type of blockchain (EVM, Solana, etc.)
            chain_class: Chain implementation class
        """
        cls._chain_classes[chain_type] = chain_class
        logger.info(f"Registered chain class {chain_class.__name__} for type {chain_type.value}")
    
    @classmethod
    async def create_chain(cls, network_name: str, **kwargs) -> BaseChain:
        """
        Create a blockchain chain instance.
        
        Args:
            network_name: Name of the network (e.g., 'ethereum', 'polygon')
            **kwargs: Additional configuration parameters
            
        Returns:
            Configured chain instance
            
        Raises:
            ChainNotSupportedException: If network is not supported
            ChainConnectionException: If chain creation fails
        """
        # Check if instance already exists
        if network_name in cls._instances:
            return cls._instances[network_name]
        
        try:
            # Get network configuration
            network_config = NetworkConfig.get_network_config(network_name)
            
            # Determine chain type
            chain_type_str = network_config.get("type", "evm")
            try:
                chain_type = ChainType(chain_type_str)
            except ValueError:
                raise ChainNotSupportedException(f"Unknown chain type: {chain_type_str}")
            
            # Get chain class
            if chain_type not in cls._chain_classes:
                raise ChainNotSupportedException(f"No implementation for chain type: {chain_type.value}")
            
            chain_class = cls._chain_classes[chain_type]
            
            # Prepare RPC URLs with API keys
            rpc_urls = cls._prepare_rpc_urls(network_name, network_config["rpc_urls"])
            
            # Create chain instance
            chain_instance = chain_class(
                network_name=network_name,
                rpc_urls=rpc_urls,
                **network_config,
                **kwargs
            )
            
            # Store instance
            cls._instances[network_name] = chain_instance
            
            logger.info(f"Created chain instance for {network_name}")
            return chain_instance
            
        except Exception as e:
            logger.error(f"Failed to create chain for {network_name}: {e}")
            raise ChainConnectionException(f"Failed to create chain: {e}")
    
    @classmethod
    async def get_chain(cls, network_name: str) -> Optional[BaseChain]:
        """
        Get an existing chain instance.
        
        Args:
            network_name: Name of the network
            
        Returns:
            Chain instance or None if not found
        """
        return cls._instances.get(network_name)
    
    @classmethod
    async def remove_chain(cls, network_name: str) -> bool:
        """
        Remove a chain instance.
        
        Args:
            network_name: Name of the network
            
        Returns:
            True if removed successfully, False if not found
        """
        if network_name in cls._instances:
            chain = cls._instances[network_name]
            await chain.disconnect()
            del cls._instances[network_name]
            logger.info(f"Removed chain instance for {network_name}")
            return True
        return False
    
    @classmethod
    async def get_all_chains(cls) -> Dict[str, BaseChain]:
        """
        Get all chain instances.
        
        Returns:
            Dictionary of network name to chain instance
        """
        return cls._instances.copy()
    
    @classmethod
    async def create_all_supported_chains(cls) -> Dict[str, BaseChain]:
        """
        Create chain instances for all supported networks.
        
        Returns:
            Dictionary of network name to chain instance
        """
        chains = {}
        for network_name in NetworkConfig.get_all_networks():
            try:
                chain = await cls.create_chain(network_name)
                chains[network_name] = chain
            except Exception as e:
                logger.error(f"Failed to create chain for {network_name}: {e}")
        
        logger.info(f"Created {len(chains)} chain instances")
        return chains
    
    @classmethod
    def _prepare_rpc_urls(cls, network_name: str, base_urls: list) -> list:
        """
        Prepare RPC URLs with API keys.
        
        Args:
            network_name: Name of the network
            base_urls: Base RPC URLs from configuration
            
        Returns:
            List of RPC URLs with API keys injected
        """
        rpc_urls = []
        
        # Add URLs with API keys from environment
        for url in base_urls:
            if "alchemy.com" in url and settings.alchemy_api_key:
                rpc_urls.append(f"{url}{settings.alchemy_api_key}")
            elif "infura.io" in url and settings.infura_api_key:
                rpc_urls.append(f"{url}{settings.infura_api_key}")
            elif "quicknode" in url and settings.quicknode_api_key:
                rpc_urls.append(f"{url}{settings.quicknode_api_key}")
            else:
                rpc_urls.append(url)
        
        # Add network-specific URLs from environment
        env_url = getattr(settings, f"{network_name}_rpc_url", None)
        if env_url and env_url not in rpc_urls:
            rpc_urls.insert(0, env_url)
        
        return rpc_urls
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, Dict]:
        """
        Perform health check on all chain instances.
        
        Returns:
            Dictionary of network name to health status
        """
        health_status = {}
        for network_name, chain in cls._instances.items():
            health_status[network_name] = await chain.health_check()
        return health_status


# Initialize and register chain classes
def initialize_chain_factory():
    """Initialize the chain factory with all available chain implementations."""
    try:
        # Import and register EVM chains
        from app.core.blockchain.evm_chains.ethereum_chain import EthereumChain
        from app.core.blockchain.evm_chains.arbitrum_chain import ArbitrumChain
        from app.core.blockchain.evm_chains.optimism_chain import OptimismChain
        from app.core.blockchain.evm_chains.base_chain import BaseChainImpl
        from app.core.blockchain.evm_chains.polygon_chain import PolygonChain
        from app.core.blockchain.evm_chains.bnb_chain import BNBChain
        from app.core.blockchain.evm_chains.avalanche_chain import AvalancheChain
        
        # Register EVM chains (they all use the same base EVM implementation)
        ChainFactory.register_chain_class(ChainType.EVM, EthereumChain)
        
        # Import and register non-EVM chains
        try:
            from app.core.blockchain.non_evm_chains.solana_chain import SolanaChain
            ChainFactory.register_chain_class(ChainType.SOLANA, SolanaChain)
        except ImportError:
            logger.warning("Solana chain implementation not available")
        
        except ImportError:
            logger.warning("Starknet chain implementation not available")
        
        try:
            from app.core.blockchain.non_evm_chains.sui_chain import SuiChain
            ChainFactory.register_chain_class(ChainType.SUI, SuiChain)
        except ImportError:
            logger.warning("Sui chain implementation not available")
        
        try:
            from app.core.blockchain.non_evm_chains.sei_chain import SeiChain
            ChainFactory.register_chain_class(ChainType.SEI, SeiChain)
        except ImportError:
            logger.warning("Sei chain implementation not available")
        
        logger.info("Chain factory initialized successfully")
        
    except ImportError as e:
        logger.error(f"Failed to initialize chain factory: {e}")
        raise


# Auto-initialize when module is imported
try:
    initialize_chain_factory()
except Exception as e:
    logger.error(f"Auto-initialization failed: {e}")