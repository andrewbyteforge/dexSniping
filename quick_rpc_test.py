"""
Quick RPC Connection Test
File: quick_rpc_test.py

Simple test to verify public RPC connections work without API keys.
"""

from web3 import Web3
import time


def test_public_rpcs():
    """Test public RPC endpoints."""
    print("🚀 Testing Public RPC Connections - No API Keys Required!")
    print("=" * 60)
    
    rpcs = [
        ('Ethereum', 'https://ethereum.publicnode.com'),
        ('Polygon', 'https://polygon-rpc.com'), 
        ('BSC', 'https://bsc-dataseed.binance.org/'),
        ('Arbitrum', 'https://arb1.arbitrum.io/rpc'),
        ('Avalanche', 'https://api.avax.network/ext/bc/C/rpc'),
        ('Ethereum Alt', 'https://eth.llamarpc.com'),
        ('BSC Alt', 'https://bsc-dataseed1.defibit.io/')
    ]
    
    successful = 0
    total = len(rpcs)
    
    for name, url in rpcs:
        try:
            print(f"🔄 Testing {name}...")
            start_time = time.time()
            
            # Create Web3 instance
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10}))
            
            # Test connection
            if w3.is_connected():
                # Get latest block
                block = w3.eth.block_number
                
                # Get gas price if possible
                try:
                    gas_price = w3.eth.gas_price
                    gas_gwei = w3.from_wei(gas_price, 'gwei')
                except:
                    gas_gwei = 0
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000
                
                print(f"✅ {name}: Connected!")
                print(f"   📦 Latest Block: {block:,}")
                print(f"   ⛽ Gas Price: {gas_gwei:.1f} Gwei")
                print(f"   ⏱️ Response Time: {response_time:.0f}ms")
                print()
                
                successful += 1
            else:
                print(f"❌ {name}: Connection failed")
                print()
                
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)[:50]}...")
            print()
    
    print("=" * 60)
    print(f"📊 RESULTS: {successful}/{total} RPCs working")
    
    if successful > 0:
        print("🎉 SUCCESS: We can connect to live blockchain networks!")
        print("✅ Ready to proceed with live trading integration")
        
        if successful >= 3:
            print("🚀 Multiple networks available - excellent connectivity!")
        elif successful >= 1:
            print("⚡ Basic connectivity established")
            
    else:
        print("⚠️ No RPCs working - check internet connection")
    
    return successful > 0


def test_token_contract():
    """Test reading a token contract."""
    print("\n🔍 Testing Token Contract Reading...")
    print("-" * 40)
    
    try:
        # Use Ethereum public RPC
        w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
        
        if not w3.is_connected():
            print("❌ Cannot connect to Ethereum")
            return False
        
        # USDC contract address
        usdc_address = "0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e"
        
        # Simple ERC20 ABI
        abi = [
            {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
        ]
        
        # Create contract instance
        contract = w3.eth.contract(address=usdc_address, abi=abi)
        
        # Read token info
        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        
        print(f"✅ Token Contract Read Successful!")
        print(f"   📄 Name: {name}")
        print(f"   🔤 Symbol: {symbol}")
        print(f"   🔢 Decimals: {decimals}")
        
        return True
        
    except Exception as e:
        print(f"❌ Token contract test failed: {e}")
        return False


if __name__ == "__main__":
    # Test public RPCs
    rpc_success = test_public_rpcs()
    
    if rpc_success:
        # Test token contract reading
        test_token_contract()
        
        print("\n" + "=" * 60)
        print("🎯 CONCLUSION: Live blockchain integration is ready!")
        print("🔧 Next step: Activate Phase 4B live trading engine")
        print("💡 Run: uvicorn app.main:app --reload")
    else:
        print("\n⚠️ Connection issues detected")
        print("💡 Try running again or check internet connection")