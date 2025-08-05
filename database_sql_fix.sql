-- Replace the _create_tables method in app/core/database/persistence_manager.py
-- with this corrected version to fix the "INDEX" syntax error

async def _create_tables(self):
    """Create all required database tables with corrected SQL syntax."""
    
    # Trades table - Fixed INDEX syntax
    await self._connection.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            trade_id TEXT PRIMARY KEY,
            wallet_address TEXT NOT NULL,
            token_in TEXT NOT NULL,
            token_out TEXT NOT NULL,
            amount_in REAL NOT NULL,
            amount_out REAL NOT NULL,
            price_usd REAL NOT NULL,
            dex_protocol TEXT NOT NULL,
            network TEXT NOT NULL,
            transaction_hash TEXT,
            status TEXT NOT NULL,
            gas_used INTEGER,
            gas_price_gwei REAL,
            slippage_percent REAL NOT NULL,
            profit_loss_usd REAL,
            created_at TEXT NOT NULL,
            executed_at TEXT
        )
    """)
    
    # Create indexes separately (this is the key fix)
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_trades_wallet ON trades(wallet_address)
    """)
    
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_trades_created_at ON trades(created_at)
    """)
    
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)
    """)
    
    # Portfolio snapshots table
    await self._connection.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            snapshot_id TEXT PRIMARY KEY,
            wallet_address TEXT NOT NULL,
            total_value_usd REAL NOT NULL,
            eth_balance REAL NOT NULL,
            token_count INTEGER NOT NULL,
            top_holdings TEXT NOT NULL,
            profit_loss_24h REAL NOT NULL,
            network TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Create indexes separately
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_portfolios_wallet ON portfolios(wallet_address)
    """)
    
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_portfolios_created_at ON portfolios(created_at)
    """)
    
    # Wallet sessions table
    await self._connection.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            session_id TEXT PRIMARY KEY,
            wallet_address TEXT NOT NULL,
            wallet_type TEXT NOT NULL,
            network TEXT NOT NULL,
            connected_at TEXT NOT NULL,
            last_activity TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            permissions TEXT NOT NULL DEFAULT '[]',
            metadata TEXT NOT NULL DEFAULT '{}'
        )
    """)
    
    # Create indexes separately
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_wallets_address ON wallets(wallet_address)
    """)
    
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_wallets_active ON wallets(is_active)
    """)
    
    # Trading opportunities table
    await self._connection.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            opportunity_id TEXT PRIMARY KEY,
            token_address TEXT NOT NULL,
            token_symbol TEXT NOT NULL,
            network TEXT NOT NULL,
            price_usd REAL NOT NULL,
            market_cap REAL,
            liquidity_usd REAL NOT NULL,
            volume_24h REAL,
            price_change_1h REAL,
            risk_score REAL NOT NULL,
            confidence_score REAL NOT NULL,
            discovered_at TEXT NOT NULL,
            expires_at TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    
    # Create indexes separately
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_opportunities_token ON opportunities(token_address)
    """)
    
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_opportunities_discovered ON opportunities(discovered_at)
    """)
    
    await self._connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_opportunities_risk ON opportunities(risk_score)
    """)
    
    # Configuration settings table
    await self._connection.execute("""
        CREATE TABLE IF NOT EXISTS configurations (
            config_key TEXT PRIMARY KEY,
            config_value TEXT NOT NULL,
            config_type TEXT NOT NULL DEFAULT 'string',
            description TEXT,
            updated_at TEXT NOT NULL,
            updated_by TEXT DEFAULT 'system'
        )
    """)
    
    await self._connection.commit()
