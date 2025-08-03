"""
Trading Database Migration Script
File: app/migrations/create_trading_tables.py

Complete migration script to create all trading-related database tables
with proper indexes, constraints, and relationships.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text


def upgrade():
    """Create trading tables and related structures."""
    
    # Create ENUM types first
    create_enums()
    
    # Create trading tables
    create_trading_orders_table()
    create_order_fills_table()
    create_trading_positions_table()
    create_portfolio_transactions_table()
    create_trading_strategies_table()
    create_risk_limits_table()
    
    # Create indexes for performance
    create_indexes()
    
    # Create foreign key constraints
    create_foreign_keys()


def downgrade():
    """Drop trading tables and related structures."""
    
    # Drop tables in reverse order
    op.drop_table('risk_limits')
    op.drop_table('trading_strategies')
    op.drop_table('portfolio_transactions')
    op.drop_table('order_fills')
    op.drop_table('trading_positions')
    op.drop_table('trading_orders')
    
    # Drop ENUM types
    drop_enums()


def create_enums():
    """Create ENUM types for trading system."""
    
    # Order side enum
    order_side_enum = postgresql.ENUM(
        'buy', 'sell',
        name='order_side',
        create_type=False
    )
    order_side_enum.create(op.get_bind(), checkfirst=True)
    
    # Order type enum
    order_type_enum = postgresql.ENUM(
        'market', 'limit', 'stop_loss', 'take_profit', 'trailing_stop',
        name='order_type',
        create_type=False
    )
    order_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Order status enum
    order_status_enum = postgresql.ENUM(
        'pending', 'open', 'partially_filled', 'filled', 'cancelled', 'rejected', 'expired',
        name='order_status',
        create_type=False
    )
    order_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Position status enum
    position_status_enum = postgresql.ENUM(
        'open', 'closed', 'partial',
        name='position_status',
        create_type=False
    )
    position_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Transaction type enum
    transaction_type_enum = postgresql.ENUM(
        'buy', 'sell', 'deposit', 'withdrawal', 'fee', 'reward',
        name='transaction_type',
        create_type=False
    )
    transaction_type_enum.create(op.get_bind(), checkfirst=True)


def create_trading_orders_table():
    """Create trading_orders table."""
    op.create_table(
        'trading_orders',
        
        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('order_id', sa.String(100), unique=True, nullable=False, index=True),
        
        # User identification
        sa.Column('user_wallet', sa.String(255), nullable=False, index=True),
        
        # Order details
        sa.Column('token_address', sa.String(255), nullable=False, index=True),
        sa.Column('token_symbol', sa.String(50), nullable=True),
        sa.Column('side', postgresql.ENUM(name='order_side'), nullable=False),
        sa.Column('order_type', postgresql.ENUM(name='order_type'), nullable=False),
        sa.Column('status', postgresql.ENUM(name='order_status'), 
                 server_default='pending', nullable=False, index=True),
        
        # Quantities and prices
        sa.Column('amount', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('filled_amount', sa.Numeric(precision=36, scale=18), 
                 server_default='0', nullable=False),
        sa.Column('price', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('average_fill_price', sa.Numeric(precision=36, scale=18), nullable=True),
        
        # Order parameters
        sa.Column('slippage_tolerance', sa.Numeric(precision=5, scale=4), 
                 server_default='0.01', nullable=False),
        sa.Column('gas_limit', sa.Integer, nullable=True),
        sa.Column('gas_price', sa.Numeric(precision=20, scale=0), nullable=True),
        
        # DEX information
        sa.Column('dex_name', sa.String(50), nullable=False),
        sa.Column('pair_address', sa.String(255), nullable=True),
        sa.Column('router_address', sa.String(255), nullable=True),
        
        # Execution details
        sa.Column('transaction_hash', sa.String(255), nullable=True, index=True),
        sa.Column('block_number', sa.Integer, nullable=True),
        sa.Column('transaction_fee', sa.Numeric(precision=36, scale=18), nullable=True),
        
        # Risk management
        sa.Column('stop_loss_price', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('take_profit_price', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('trailing_stop_distance', sa.Numeric(precision=10, scale=4), nullable=True),
        
        # Timing
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Additional data
        sa.Column('order_metadata', sa.JSON, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
    )


def create_order_fills_table():
    """Create order_fills table."""
    op.create_table(
        'order_fills',
        
        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('fill_id', sa.String(100), unique=True, nullable=False, index=True),
        
        # Foreign key to order
        sa.Column('order_id', sa.Integer, nullable=False, index=True),
        
        # Fill details
        sa.Column('amount', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('price', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('total_value', sa.Numeric(precision=36, scale=18), nullable=False),
        
        # Execution details
        sa.Column('transaction_hash', sa.String(255), nullable=False, index=True),
        sa.Column('block_number', sa.Integer, nullable=False),
        sa.Column('transaction_index', sa.Integer, nullable=True),
        sa.Column('log_index', sa.Integer, nullable=True),
        
        # Fees
        sa.Column('gas_used', sa.Integer, nullable=True),
        sa.Column('gas_price', sa.Numeric(precision=20, scale=0), nullable=True),
        sa.Column('transaction_fee', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('dex_fee', sa.Numeric(precision=36, scale=18), nullable=True),
        
        # Timing
        sa.Column('filled_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), nullable=False, index=True),
        
        # Additional data
        sa.Column('fill_metadata', sa.JSON, nullable=True),
    )


def create_trading_positions_table():
    """Create trading_positions table."""
    op.create_table(
        'trading_positions',
        
        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('position_id', sa.String(100), unique=True, nullable=False, index=True),
        
        # User identification
        sa.Column('user_wallet', sa.String(255), nullable=False, index=True),
        
        # Position details
        sa.Column('token_address', sa.String(255), nullable=False, index=True),
        sa.Column('token_symbol', sa.String(50), nullable=True),
        sa.Column('status', postgresql.ENUM(name='position_status'), 
                 server_default='open', nullable=False, index=True),
        
        # Position quantities
        sa.Column('total_quantity', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('remaining_quantity', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('average_entry_price', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('average_exit_price', sa.Numeric(precision=36, scale=18), nullable=True),
        
        # Position value
        sa.Column('total_cost', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('total_fees', sa.Numeric(precision=36, scale=18), 
                 server_default='0', nullable=False),
        sa.Column('realized_pnl', sa.Numeric(precision=36, scale=18), 
                 server_default='0', nullable=False),
        sa.Column('unrealized_pnl', sa.Numeric(precision=36, scale=18), 
                 server_default='0', nullable=False),
        
        # Risk management
        sa.Column('stop_loss_price', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('take_profit_price', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('max_drawdown', sa.Numeric(precision=10, scale=4), 
                 server_default='0', nullable=False),
        
        # Timing
        sa.Column('opened_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Additional data
        sa.Column('strategy_name', sa.String(100), nullable=True),
        sa.Column('position_metadata', sa.JSON, nullable=True),
    )


def create_portfolio_transactions_table():
    """Create portfolio_transactions table."""
    op.create_table(
        'portfolio_transactions',
        
        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('transaction_id', sa.String(100), unique=True, nullable=False, index=True),
        
        # User identification
        sa.Column('user_wallet', sa.String(255), nullable=False, index=True),
        
        # Transaction details
        sa.Column('transaction_type', postgresql.ENUM(name='transaction_type'), 
                 nullable=False, index=True),
        sa.Column('token_address', sa.String(255), nullable=False, index=True),
        sa.Column('token_symbol', sa.String(50), nullable=True),
        
        # Amounts
        sa.Column('amount', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('price_per_token', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('total_value_usd', sa.Numeric(precision=36, scale=18), nullable=True),
        
        # Blockchain details
        sa.Column('transaction_hash', sa.String(255), nullable=True, index=True),
        sa.Column('block_number', sa.Integer, nullable=True),
        sa.Column('dex_name', sa.String(50), nullable=True),
        
        # Fees
        sa.Column('gas_fee', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('dex_fee', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('slippage', sa.Numeric(precision=10, scale=4), nullable=True),
        
        # Position reference
        sa.Column('position_id', sa.Integer, nullable=True, index=True),
        
        # Timing
        sa.Column('executed_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), nullable=False, index=True),
        
        # Additional data
        sa.Column('transaction_metadata', sa.JSON, nullable=True),
    )


def create_trading_strategies_table():
    """Create trading_strategies table."""
    op.create_table(
        'trading_strategies',
        
        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('strategy_id', sa.String(100), unique=True, nullable=False, index=True),
        
        # User identification
        sa.Column('user_wallet', sa.String(255), nullable=False, index=True),
        
        # Strategy details
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('strategy_type', sa.String(50), nullable=False, index=True),
        sa.Column('status', sa.String(20), server_default='active', nullable=False, index=True),
        
        # Strategy parameters
        sa.Column('parameters', sa.JSON, nullable=False),
        sa.Column('risk_parameters', sa.JSON, nullable=True),
        
        # Performance tracking
        sa.Column('total_trades', sa.Integer, server_default='0', nullable=False),
        sa.Column('winning_trades', sa.Integer, server_default='0', nullable=False),
        sa.Column('total_volume', sa.Numeric(precision=36, scale=18), 
                 server_default='0', nullable=False),
        sa.Column('total_pnl', sa.Numeric(precision=36, scale=18), 
                 server_default='0', nullable=False),
        sa.Column('max_drawdown', sa.Numeric(precision=10, scale=4), 
                 server_default='0', nullable=False),
        
        # Timing
        sa.Column('created_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('last_executed_at', sa.DateTime(timezone=True), nullable=True),
    )


def create_risk_limits_table():
    """Create risk_limits table."""
    op.create_table(
        'risk_limits',
        
        # Primary key
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        
        # User identification
        sa.Column('user_wallet', sa.String(255), nullable=False, index=True),
        
        # Position limits
        sa.Column('max_position_size', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('max_position_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('max_open_positions', sa.Integer, nullable=True),
        
        # Risk limits
        sa.Column('max_daily_loss', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('max_drawdown_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('stop_loss_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        
        # Trading limits
        sa.Column('max_daily_trades', sa.Integer, nullable=True),
        sa.Column('max_slippage', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('min_liquidity_usd', sa.Numeric(precision=36, scale=18), nullable=True),
        
        # Token restrictions
        sa.Column('blacklisted_tokens', sa.JSON, nullable=True),
        sa.Column('whitelisted_tokens', sa.JSON, nullable=True),
        sa.Column('max_risk_score', sa.Numeric(precision=4, scale=2), nullable=True),
        
        # Settings
        sa.Column('auto_stop_loss', sa.Boolean, server_default='true', nullable=False),
        sa.Column('auto_take_profit', sa.Boolean, server_default='false', nullable=False),
        sa.Column('emergency_stop', sa.Boolean, server_default='false', nullable=False),
        
        # Timing
        sa.Column('created_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Unique constraint
        sa.UniqueConstraint('user_wallet', name='uq_risk_limits_user_wallet'),
    )


def create_indexes():
    """Create performance indexes."""
    
    # Trading orders indexes
    op.create_index('idx_orders_user_status', 'trading_orders', ['user_wallet', 'status'])
    op.create_index('idx_orders_token_created', 'trading_orders', ['token_address', 'created_at'])
    op.create_index('idx_orders_dex_status', 'trading_orders', ['dex_name', 'status'])
    op.create_index('idx_orders_created_status', 'trading_orders', ['created_at', 'status'])
    
    # Order fills indexes
    op.create_index('idx_fills_order_filled', 'order_fills', ['order_id', 'filled_at'])
    op.create_index('idx_fills_tx_hash', 'order_fills', ['transaction_hash'])
    
    # Trading positions indexes
    op.create_index('idx_positions_user_status', 'trading_positions', ['user_wallet', 'status'])
    op.create_index('idx_positions_token_opened', 'trading_positions', ['token_address', 'opened_at'])
    op.create_index('idx_positions_strategy', 'trading_positions', ['strategy_name'])
    
    # Portfolio transactions indexes
    op.create_index('idx_transactions_user_type', 'portfolio_transactions', 
                   ['user_wallet', 'transaction_type'])
    op.create_index('idx_transactions_token_executed', 'portfolio_transactions', 
                   ['token_address', 'executed_at'])
    op.create_index('idx_transactions_position', 'portfolio_transactions', ['position_id'])
    
    # Trading strategies indexes
    op.create_index('idx_strategies_user_type', 'trading_strategies', 
                   ['user_wallet', 'strategy_type'])
    op.create_index('idx_strategies_status', 'trading_strategies', ['status'])


def create_foreign_keys():
    """Create foreign key constraints."""
    
    # Order fills -> Trading orders
    op.create_foreign_key(
        'fk_order_fills_order_id',
        'order_fills', 'trading_orders',
        ['order_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Portfolio transactions -> Trading positions
    op.create_foreign_key(
        'fk_portfolio_transactions_position_id',
        'portfolio_transactions', 'trading_positions',
        ['position_id'], ['id'],
        ondelete='SET NULL'
    )


def drop_enums():
    """Drop ENUM types."""
    op.execute('DROP TYPE IF EXISTS order_side CASCADE')
    op.execute('DROP TYPE IF EXISTS order_type CASCADE')
    op.execute('DROP TYPE IF EXISTS order_status CASCADE')
    op.execute('DROP TYPE IF EXISTS position_status CASCADE')
    op.execute('DROP TYPE IF EXISTS transaction_type CASCADE')


def create_sample_data():
    """Create sample data for testing (optional)."""
    
    # Sample risk limits for a test user
    sample_risk_limits = {
        'user_wallet': '0x742d35Cc6345d4B424dA44A56ad419a8f93b9b2e',
        'max_position_size': '1000.00',
        'max_position_percentage': '10.00',
        'max_open_positions': 20,
        'max_daily_loss': '50.00',
        'max_drawdown_percentage': '20.00',
        'max_daily_trades': 100,
        'max_slippage': '0.05',
        'min_liquidity_usd': '10000.00',
        'max_risk_score': '7.00',
        'auto_stop_loss': True,
        'auto_take_profit': False,
        'emergency_stop': False,
        'blacklisted_tokens': '[]',
        'whitelisted_tokens': None
    }
    
    op.execute(
        text("""
            INSERT INTO risk_limits (
                user_wallet, max_position_size, max_position_percentage, 
                max_open_positions, max_daily_loss, max_drawdown_percentage,
                max_daily_trades, max_slippage, min_liquidity_usd, max_risk_score,
                auto_stop_loss, auto_take_profit, emergency_stop,
                blacklisted_tokens, whitelisted_tokens
            ) VALUES (
                :user_wallet, :max_position_size, :max_position_percentage,
                :max_open_positions, :max_daily_loss, :max_drawdown_percentage,
                :max_daily_trades, :max_slippage, :min_liquidity_usd, :max_risk_score,
                :auto_stop_loss, :auto_take_profit, :emergency_stop,
                :blacklisted_tokens, :whitelisted_tokens
            )
        """),
        sample_risk_limits
    )


def verify_migration():
    """Verify that all tables were created successfully."""
    connection = op.get_bind()
    
    required_tables = [
        'trading_orders',
        'order_fills', 
        'trading_positions',
        'portfolio_transactions',
        'trading_strategies',
        'risk_limits'
    ]
    
    for table_name in required_tables:
        result = connection.execute(
            text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                );
            """)
        )
        
        if not result.fetchone()[0]:
            raise Exception(f"Table {table_name} was not created successfully")
    
    print("✅ All trading tables created successfully!")


if __name__ == "__main__":
    """Run migration when script is executed directly."""
    print("🚀 Running trading database migration...")
    
    try:
        upgrade()
        verify_migration()
        print("🎉 Trading database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("🔄 Attempting rollback...")
        try:
            downgrade()
            print("✅ Rollback completed")
        except Exception as rollback_error:
            print(f"❌ Rollback failed: {rollback_error}")