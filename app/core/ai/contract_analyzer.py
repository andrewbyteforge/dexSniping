"""
AI Contract Analyzer
File: app/core/ai/contract_analyzer.py

Advanced smart contract analysis engine for comprehensive security evaluation,
bytecode analysis, and trading viability assessment.
"""

import asyncio
import re
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from app.utils.logger import setup_logger
from app.core.exceptions import ContractAnalysisError, ValidationError
from app.core.blockchain.base_chain import BaseChain

logger = setup_logger(__name__, "application")


class ContractType(Enum):
    """Smart contract classification types."""
    STANDARD_ERC20 = "standard_erc20"
    DEFLATIONARY = "deflationary"
    REBASE = "rebase"
    REFLECTION = "reflection"
    LIQUIDITY_TOKEN = "liquidity_token"
    WRAPPED_TOKEN = "wrapped_token"
    GOVERNANCE_TOKEN = "governance_token"
    MEME_TOKEN = "meme_token"
    UTILITY_TOKEN = "utility_token"
    HONEYPOT = "honeypot"
    RUGPULL = "rugpull"
    UNKNOWN = "unknown"


class SecurityRisk(Enum):
    """Security risk levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContractFunction:
    """Smart contract function analysis."""
    name: str
    selector: str
    visibility: str
    modifiers: List[str]
    parameters: List[str]
    is_payable: bool
    is_suspicious: bool
    risk_score: float


@dataclass
class ContractAnalysis:
    """Comprehensive contract analysis results."""
    token_address: str
    network: str
    contract_type: ContractType
    security_risk: SecurityRisk
    risk_score: float
    confidence: float
    
    # Contract metadata
    name: str
    symbol: str
    decimals: int
    total_supply: Decimal
    max_supply: Optional[Decimal]
    
    # Code analysis
    source_code_verified: bool
    compiler_version: Optional[str]
    optimization_enabled: bool
    proxy_contract: bool
    
    # Ownership analysis
    has_owner: bool
    owner_address: Optional[str]
    ownership_renounced: bool
    owner_privileges: List[str]
    
    # Token mechanics
    has_mint_function: bool
    has_burn_function: bool
    has_pause_function: bool
    has_blacklist_function: bool
    has_transfer_fees: bool
    transfer_fee_percentage: float
    
    # Liquidity analysis
    liquidity_locked: bool
    liquidity_lock_duration: Optional[timedelta]
    initial_liquidity_usd: float
    current_liquidity_usd: float
    
    # Trading analysis
    can_buy: bool
    can_sell: bool
    max_transaction_amount: Optional[Decimal]
    cooldown_period: Optional[int]
    
    # Security flags
    honeypot_indicators: List[str]
    rugpull_indicators: List[str]
    suspicious_functions: List[ContractFunction]
    
    # Social presence
    website_url: Optional[str]
    twitter_handle: Optional[str]
    telegram_group: Optional[str]
    
    # Analysis metadata
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    analysis_duration_ms: int = 0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ContractAnalyzer:
    """
    Advanced smart contract analyzer with security focus.
    
    Features:
    - Bytecode disassembly and analysis
    - Function signature detection
    - Ownership pattern analysis
    - Liquidity security assessment
    - Honeypot detection algorithms
    - Trading viability scoring
    """
    
    def __init__(self):
        """Initialize contract analyzer."""
        self.known_signatures = self._load_function_signatures()
        self.honeypot_patterns = self._load_honeypot_patterns()
        self.suspicious_patterns = self._load_suspicious_patterns()
        logger.info("[OK] Contract Analyzer initialized")
    
    async def analyze_contract(
        self,
        token_address: str,
        network: str,
        chain: BaseChain
    ) -> ContractAnalysis:
        """
        Perform comprehensive contract analysis.
        
        Args:
            token_address: Contract address to analyze
            network: Blockchain network
            chain: Blockchain instance
            
        Returns:
            ContractAnalysis: Complete analysis results
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"[SEARCH] Starting contract analysis for {token_address}")
            
            # Get basic token information
            token_info = await chain.get_token_info(token_address)
            
            # Get contract bytecode
            bytecode = await chain.get_contract_bytecode(token_address)
            
            # Get source code if available
            source_code = await chain.get_contract_source_code(token_address)
            
            # Analyze contract structure
            contract_type = await self._classify_contract_type(
                token_address, bytecode, source_code, chain
            )
            
            # Analyze security aspects
            security_analysis = await self._analyze_security(
                token_address, bytecode, source_code, chain
            )
            
            # Analyze ownership
            ownership_analysis = await self._analyze_ownership(
                token_address, bytecode, source_code, chain
            )
            
            # Analyze liquidity
            liquidity_analysis = await self._analyze_liquidity(
                token_address, network, chain
            )
            
            # Analyze trading mechanics
            trading_analysis = await self._analyze_trading_mechanics(
                token_address, bytecode, source_code, chain
            )
            
            # Calculate overall risk score
            risk_score, security_risk, confidence = self._calculate_risk_score(
                security_analysis, ownership_analysis, liquidity_analysis, trading_analysis
            )
            
            # Generate warnings and recommendations
            warnings, recommendations = self._generate_insights(
                security_analysis, ownership_analysis, liquidity_analysis, trading_analysis
            )
            
            # Calculate analysis duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Create comprehensive analysis result
            analysis = ContractAnalysis(
                token_address=token_address,
                network=network,
                contract_type=contract_type,
                security_risk=security_risk,
                risk_score=risk_score,
                confidence=confidence,
                
                # Token metadata
                name=token_info.get('name', 'Unknown'),
                symbol=token_info.get('symbol', 'Unknown'),
                decimals=token_info.get('decimals', 18),
                total_supply=Decimal(str(token_info.get('total_supply', 0))),
                max_supply=None,
                
                # Code analysis
                source_code_verified=source_code is not None,
                compiler_version=security_analysis.get('compiler_version'),
                optimization_enabled=security_analysis.get('optimization_enabled', False),
                proxy_contract=security_analysis.get('is_proxy', False),
                
                # Ownership
                has_owner=ownership_analysis.get('has_owner', False),
                owner_address=ownership_analysis.get('owner_address'),
                ownership_renounced=ownership_analysis.get('renounced', False),
                owner_privileges=ownership_analysis.get('privileges', []),
                
                # Token mechanics
                has_mint_function=security_analysis.get('has_mint', False),
                has_burn_function=security_analysis.get('has_burn', False),
                has_pause_function=security_analysis.get('has_pause', False),
                has_blacklist_function=security_analysis.get('has_blacklist', False),
                has_transfer_fees=trading_analysis.get('has_fees', False),
                transfer_fee_percentage=trading_analysis.get('fee_percentage', 0.0),
                
                # Liquidity
                liquidity_locked=liquidity_analysis.get('locked', False),
                liquidity_lock_duration=liquidity_analysis.get('lock_duration'),
                initial_liquidity_usd=liquidity_analysis.get('initial_liquidity', 0.0),
                current_liquidity_usd=liquidity_analysis.get('current_liquidity', 0.0),
                
                # Trading
                can_buy=trading_analysis.get('can_buy', True),
                can_sell=trading_analysis.get('can_sell', True),
                max_transaction_amount=trading_analysis.get('max_tx_amount'),
                cooldown_period=trading_analysis.get('cooldown'),
                
                # Security flags
                honeypot_indicators=security_analysis.get('honeypot_indicators', []),
                rugpull_indicators=security_analysis.get('rugpull_indicators', []),
                suspicious_functions=security_analysis.get('suspicious_functions', []),
                
                # Social presence (would be fetched from additional sources)
                website_url=None,
                twitter_handle=None,
                telegram_group=None,
                
                # Metadata
                analysis_timestamp=start_time,
                analysis_duration_ms=duration_ms,
                warnings=warnings,
                recommendations=recommendations
            )
            
            logger.info(f"[OK] Contract analysis complete for {token_address} - "
                       f"Risk: {security_risk.value}, Score: {risk_score:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"[ERROR] Contract analysis failed for {token_address}: {e}")
            raise ContractAnalysisError(f"Analysis failed: {e}")
    
    async def _classify_contract_type(
        self,
        token_address: str,
        bytecode: str,
        source_code: Optional[str],
        chain: BaseChain
    ) -> ContractType:
        """Classify the contract type based on analysis."""
        try:
            # Analyze function signatures
            functions = self._extract_function_signatures(bytecode)
            
            # Check for specific patterns
            if 'transfer' not in functions and 'transferFrom' not in functions:
                return ContractType.HONEYPOT
            
            if 'rebase' in functions or 'setRebaseRate' in functions:
                return ContractType.REBASE
            
            if 'reflect' in functions or 'reflectFee' in functions:
                return ContractType.REFLECTION
            
            if 'deflate' in functions or '_taxAmount' in str(source_code):
                return ContractType.DEFLATIONARY
            
            # Default to standard ERC20
            return ContractType.STANDARD_ERC20
            
        except Exception as e:
            logger.warning(f"Failed to classify contract type: {e}")
            return ContractType.UNKNOWN
    
    async def _analyze_security(
        self,
        token_address: str,
        bytecode: str,
        source_code: Optional[str],
        chain: BaseChain
    ) -> Dict[str, Any]:
        """Analyze contract security aspects."""
        security_data = {
            'honeypot_indicators': [],
            'rugpull_indicators': [],
            'suspicious_functions': [],
            'has_mint': False,
            'has_burn': False,
            'has_pause': False,
            'has_blacklist': False,
            'is_proxy': False
        }
        
        try:
            # Extract function signatures
            functions = self._extract_function_signatures(bytecode)
            
            # Check for concerning functions
            if 'mint' in functions:
                security_data['has_mint'] = True
                security_data['rugpull_indicators'].append('Unlimited minting capability')
            
            if 'pause' in functions or 'setPaused' in functions:
                security_data['has_pause'] = True
                security_data['honeypot_indicators'].append('Contract can be paused')
            
            if 'blacklist' in functions or 'isBlacklisted' in functions:
                security_data['has_blacklist'] = True
                security_data['honeypot_indicators'].append('Blacklist functionality detected')
            
            # Check for proxy patterns
            if 'delegatecall' in bytecode.lower():
                security_data['is_proxy'] = True
                security_data['rugpull_indicators'].append('Proxy contract - implementation can change')
            
            # Analyze source code if available
            if source_code:
                security_data.update(self._analyze_source_code_security(source_code))
            
            return security_data
            
        except Exception as e:
            logger.warning(f"Security analysis failed: {e}")
            return security_data
    
    async def _analyze_ownership(
        self,
        token_address: str,
        bytecode: str,
        source_code: Optional[str],
        chain: BaseChain
    ) -> Dict[str, Any]:
        """Analyze contract ownership structure."""
        ownership_data = {
            'has_owner': False,
            'owner_address': None,
            'renounced': False,
            'privileges': []
        }
        
        try:
            # Check for owner functions
            functions = self._extract_function_signatures(bytecode)
            
            if 'owner' in functions:
                ownership_data['has_owner'] = True
                ownership_data['privileges'].append('Contract has owner')
            
            if 'onlyOwner' in str(source_code):
                ownership_data['privileges'].append('Owner-only functions detected')
            
            if 'renounceOwnership' in functions:
                ownership_data['privileges'].append('Ownership can be renounced')
            
            # Try to get current owner
            try:
                owner = await chain.call_contract_function(token_address, 'owner', [])
                if owner and owner != '0x0000000000000000000000000000000000000000':
                    ownership_data['owner_address'] = owner
                else:
                    ownership_data['renounced'] = True
            except:
                pass
            
            return ownership_data
            
        except Exception as e:
            logger.warning(f"Ownership analysis failed: {e}")
            return ownership_data
    
    async def _analyze_liquidity(
        self,
        token_address: str,
        network: str,
        chain: BaseChain
    ) -> Dict[str, Any]:
        """Analyze liquidity security."""
        liquidity_data = {
            'locked': False,
            'lock_duration': None,
            'initial_liquidity': 0.0,
            'current_liquidity': 0.0
        }
        
        try:
            # Get liquidity information from DEX
            liquidity_info = await chain.get_token_liquidity(token_address)
            
            if liquidity_info:
                liquidity_data['current_liquidity'] = float(liquidity_info.get('total_liquidity_usd', 0))
                
                # Check if liquidity is locked (simplified check)
                # In real implementation, would check specific locker contracts
                if liquidity_data['current_liquidity'] > 10000:  # $10k threshold
                    liquidity_data['locked'] = True
            
            return liquidity_data
            
        except Exception as e:
            logger.warning(f"Liquidity analysis failed: {e}")
            return liquidity_data
    
    async def _analyze_trading_mechanics(
        self,
        token_address: str,
        bytecode: str,
        source_code: Optional[str],
        chain: BaseChain
    ) -> Dict[str, Any]:
        """Analyze trading mechanics and restrictions."""
        trading_data = {
            'can_buy': True,
            'can_sell': True,
            'has_fees': False,
            'fee_percentage': 0.0,
            'max_tx_amount': None,
            'cooldown': None
        }
        
        try:
            # Check for transfer restrictions in source code
            if source_code:
                if '_taxFee' in source_code or '_liquidityFee' in source_code:
                    trading_data['has_fees'] = True
                
                # Look for fee percentages
                fee_match = re.search(r'_taxFee\s*=\s*(\d+)', source_code)
                if fee_match:
                    trading_data['fee_percentage'] = float(fee_match.group(1))
                
                # Check for transaction limits
                if 'maxTxAmount' in source_code:
                    trading_data['max_tx_amount'] = True
                
                # Check for sell restrictions
                if 'cannot sell' in source_code.lower() or 'selling disabled' in source_code.lower():
                    trading_data['can_sell'] = False
            
            return trading_data
            
        except Exception as e:
            logger.warning(f"Trading mechanics analysis failed: {e}")
            return trading_data
    
    def _calculate_risk_score(
        self,
        security_analysis: Dict[str, Any],
        ownership_analysis: Dict[str, Any],
        liquidity_analysis: Dict[str, Any],
        trading_analysis: Dict[str, Any]
    ) -> Tuple[float, SecurityRisk, float]:
        """Calculate overall risk score."""
        risk_score = 0.0
        confidence = 1.0
        
        # Security risks
        risk_score += len(security_analysis.get('honeypot_indicators', [])) * 2.0
        risk_score += len(security_analysis.get('rugpull_indicators', [])) * 2.5
        
        # Ownership risks
        if ownership_analysis.get('has_owner') and not ownership_analysis.get('renounced'):
            risk_score += 3.0
        
        # Liquidity risks
        if not liquidity_analysis.get('locked'):
            risk_score += 2.0
        
        if liquidity_analysis.get('current_liquidity', 0) < 10000:
            risk_score += 1.5
        
        # Trading risks
        if not trading_analysis.get('can_sell'):
            risk_score += 5.0  # Major red flag
        
        if trading_analysis.get('fee_percentage', 0) > 10:
            risk_score += 1.0
        
        # Normalize to 0-10 scale
        risk_score = min(10.0, max(0.0, risk_score))
        
        # Determine risk level
        if risk_score < 2.0:
            security_risk = SecurityRisk.MINIMAL
        elif risk_score < 4.0:
            security_risk = SecurityRisk.LOW
        elif risk_score < 6.0:
            security_risk = SecurityRisk.MEDIUM
        elif risk_score < 8.0:
            security_risk = SecurityRisk.HIGH
        else:
            security_risk = SecurityRisk.CRITICAL
        
        return risk_score, security_risk, confidence
    
    def _generate_insights(
        self,
        security_analysis: Dict[str, Any],
        ownership_analysis: Dict[str, Any],
        liquidity_analysis: Dict[str, Any],
        trading_analysis: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Generate warnings and recommendations."""
        warnings = []
        recommendations = []
        
        # Security warnings
        if security_analysis.get('honeypot_indicators'):
            warnings.extend(security_analysis['honeypot_indicators'])
        
        if security_analysis.get('rugpull_indicators'):
            warnings.extend(security_analysis['rugpull_indicators'])
        
        # Ownership warnings
        if ownership_analysis.get('has_owner') and not ownership_analysis.get('renounced'):
            warnings.append("Contract has active owner with privileges")
        
        # Liquidity warnings
        if not liquidity_analysis.get('locked'):
            warnings.append("Liquidity is not locked")
        
        # Trading warnings
        if not trading_analysis.get('can_sell'):
            warnings.append("CRITICAL: Token cannot be sold")
        
        # Generate recommendations
        if warnings:
            recommendations.append("Exercise extreme caution with this token")
            recommendations.append("Consider waiting for more favorable conditions")
        
        if liquidity_analysis.get('current_liquidity', 0) < 50000:
            recommendations.append("Low liquidity - expect high slippage")
        
        return warnings, recommendations
    
    def _extract_function_signatures(self, bytecode: str) -> Set[str]:
        """Extract function signatures from bytecode."""
        signatures = set()
        
        try:
            # Look for 4-byte function selectors
            selectors = re.findall(r'63([a-fA-F0-9]{8})', bytecode)
            
            for selector in selectors:
                if selector in self.known_signatures:
                    signatures.add(self.known_signatures[selector])
            
        except Exception as e:
            logger.warning(f"Failed to extract function signatures: {e}")
        
        return signatures
    
    def _analyze_source_code_security(self, source_code: str) -> Dict[str, Any]:
        """Analyze source code for security issues."""
        security_data = {}
        
        try:
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, source_code, re.IGNORECASE):
                    security_data.setdefault('suspicious_patterns', []).append(pattern)
            
            # Check for compiler version
            version_match = re.search(r'pragma solidity\s+([^\s;]+)', source_code)
            if version_match:
                security_data['compiler_version'] = version_match.group(1)
            
        except Exception as e:
            logger.warning(f"Source code analysis failed: {e}")
        
        return security_data
    
    def _load_function_signatures(self) -> Dict[str, str]:
        """Load known function signatures."""
        # In production, this would load from a comprehensive database
        return {
            'a9059cbb': 'transfer',
            '23b872dd': 'transferFrom',
            '095ea7b3': 'approve',
            '70a08231': 'balanceOf',
            '18160ddd': 'totalSupply',
            '8da5cb5b': 'owner',
            '40c10f19': 'mint',
            '42966c68': 'burn',
            '5c975abb': 'pause',
            '3f4ba83a': 'unpause',
            'f2fde38b': 'transferOwnership',
            '715018a6': 'renounceOwnership'
        }
    
    def _load_honeypot_patterns(self) -> List[str]:
        """Load known honeypot patterns."""
        return [
            r'require\s*\(\s*isBlacklisted\s*\[',
            r'require\s*\(\s*_taxFee\s*<\s*100',
            r'if\s*\(\s*from\s*!=\s*owner\s*\)',
            r'revert\s*\(\s*["\']Transfer not allowed',
        ]
    
    def _load_suspicious_patterns(self) -> List[str]:
        """Load suspicious code patterns."""
        return [
            r'selfdestruct\s*\(',
            r'delegatecall\s*\(',
            r'suicide\s*\(',
            r'require\s*\(\s*msg\.sender\s*==\s*owner',
        ]


# Factory function
async def create_contract_analyzer() -> ContractAnalyzer:
    """Create and initialize contract analyzer."""
    analyzer = ContractAnalyzer()
    return analyzer