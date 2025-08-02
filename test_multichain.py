import asyncio
from app.core.blockchain.multi_chain_manager import MultiChainManager

async def test_multi_chain():
    manager = MultiChainManager()
    print('Testing multi-chain initialization...')
    await manager.initialize(['ethereum', 'polygon'])
    networks = await manager.get_enabled_networks()
    print(f'Enabled networks: {list(networks)}')
    health = await manager.get_health_status()
    for network, status in health.items():
        print(f'{network}: {status.status.value}')
    await manager.close()
    print('Test completed!')

if __name__ == "__main__":
    asyncio.run(test_multi_chain())
