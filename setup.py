#!/usr/bin/env python3
"""
Setup Script for DEX Sniper Pro
File: setup.py

Installs compatible dependencies and sets up the development environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str = None):
    """Run a command and handle errors."""
    if description:
        print(f"📦 {description}...")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ Success: {description or command}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description or command}")
        print(f"Command: {command}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None


def setup_environment():
    """Set up the development environment."""
    print("🚀 Setting up DEX Sniper Pro development environment...")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Consider running: python -m venv venv && venv\\Scripts\\activate")
    
    # Upgrade pip first
    run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )
    
    # Uninstall conflicting packages first
    conflicting_packages = [
        "web3",
        "eth-account", 
        "eth-utils",
        "eth-typing",
        "eth-hash",
        "eth-abi"
    ]
    
    for package in conflicting_packages:
        run_command(
            f"{sys.executable} -m pip uninstall {package} -y",
            f"Removing existing {package}"
        )
    
    # Install compatible versions in correct order
    installation_order = [
        ("eth-typing==3.6.0", "Installing eth-typing"),
        ("eth-utils==2.3.1", "Installing eth-utils"),
        ("eth-hash[pycryptodome]==0.5.2", "Installing eth-hash"),
        ("eth-abi==4.2.1", "Installing eth-abi"),
        ("eth-account==0.10.0", "Installing eth-account"),
        ("web3==6.11.3", "Installing web3"),
    ]
    
    for package, description in installation_order:
        result = run_command(
            f"{sys.executable} -m pip install {package}",
            description
        )
        if result is None:
            print(f"❌ Failed to install {package}")
            return False
    
    # Install remaining requirements
    if Path("requirements.txt").exists():
        result = run_command(
            f"{sys.executable} -m pip install -r requirements.txt",
            "Installing remaining requirements"
        )
        if result is None:
            print("❌ Failed to install requirements")
            return False
    else:
        print("⚠️  requirements.txt not found, installing core packages...")
        core_packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "pydantic==2.5.0",
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "python-dotenv==1.0.0",
            "loguru==0.7.2"
        ]
        
        for package in core_packages:
            run_command(
                f"{sys.executable} -m pip install {package}",
                f"Installing {package.split('==')[0]}"
            )
    
    print("\n✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Run tests: python -m pytest tests/test_trading_engine.py -v")
    print("2. Start API: python -m uvicorn app.main:app --reload")
    print("3. Check status: python -c \"import web3; print('Web3 version:', web3.__version__)\"")
    
    return True


def verify_installation():
    """Verify that the installation was successful."""
    print("\n🔍 Verifying installation...")
    
    test_imports = [
        ("web3", "Web3 blockchain library"),
        ("eth_account", "Ethereum account management"),
        ("fastapi", "FastAPI web framework"),
        ("pytest", "Testing framework"),
        ("pydantic", "Data validation"),
        ("uvicorn", "ASGI server")
    ]
    
    failed_imports = []
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Try running the setup again or install manually:")
        for module in failed_imports:
            print(f"  pip install {module}")
        return False
    
    print("\n✅ All imports successful!")
    return True


def create_test_runner():
    """Create a test runner script."""
    test_script = """#!/usr/bin/env python3
'''
Test Runner for DEX Sniper Pro
Run with: python run_tests.py
'''

import subprocess
import sys

def run_tests():
    '''Run the test suite with proper configuration.'''
    print("🧪 Running DEX Sniper Pro test suite...")
    
    # Set environment variables for testing
    import os
    os.environ['TESTING'] = '1'
    os.environ['WEB3_TESTING'] = '1'
    
    try:
        # Run tests with verbose output
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/test_trading_engine.py',
            '-v',
            '--tb=short',
            '--no-header'
        ], check=False)
        
        if result.returncode == 0:
            print("\\n✅ All tests passed!")
        else:
            print(f"\\n❌ Tests failed with code {result.returncode}")
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Test file not found. Make sure tests/test_trading_engine.py exists")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
"""
    
    with open("run_tests.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created run_tests.py script")


if __name__ == "__main__":
    print("🤖 DEX Sniper Pro Setup")
    print("=" * 50)
    
    success = setup_environment()
    
    if success:
        verify_installation()
        create_test_runner()
        
        print("\n🎉 Setup completed successfully!")
        print("\n🧪 To run tests: python run_tests.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)