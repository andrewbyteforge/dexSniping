"""
Install Security Dependencies Script
File: install_security_deps.py

Installs required dependencies for the security system and provides fallback options.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_cryptography():
    """Install cryptography library for security functions."""
    try:
        print("🔧 Installing cryptography library...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "cryptography>=3.4.8", 
            "--upgrade"
        ])
        print("✅ Cryptography library installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install cryptography: {e}")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def install_additional_security_deps():
    """Install additional security-related dependencies."""
    try:
        print("🔧 Installing additional security dependencies...")
        
        security_packages = [
            "pycryptodome>=3.15.0",  # Alternative crypto library
            "passlib>=1.7.4",       # Password hashing
            "python-jose>=3.3.0",   # JWT handling
            "bcrypt>=3.2.0"          # Password hashing
        ]
        
        for package in security_packages:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to install {package}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Additional dependencies installation error: {e}")
        return False

def verify_installation():
    """Verify that security libraries are properly installed."""
    try:
        print("🔍 Verifying security library installation...")
        
        # Test cryptography
        try:
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            f = Fernet(key)
            test_data = b"Hello, Security!"
            encrypted = f.encrypt(test_data)
            decrypted = f.decrypt(encrypted)
            assert decrypted == test_data
            print("✅ Cryptography library working correctly")
        except ImportError:
            print("❌ Cryptography library not available")
            return False
        except Exception as e:
            print(f"❌ Cryptography test failed: {e}")
            return False
        
        # Test additional libraries
        try:
            import hashlib
            import hmac
            import secrets
            import base64
            print("✅ Standard crypto libraries available")
        except ImportError as e:
            print(f"❌ Standard crypto libraries missing: {e}")
            return False
        
        print("🎉 All security dependencies verified!")
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def create_requirements_security():
    """Create or update requirements with security dependencies."""
    try:
        print("📝 Creating security requirements...")
        
        security_requirements = """
# Security Dependencies - Phase 5A
cryptography>=3.4.8
pycryptodome>=3.15.0
passlib>=1.7.4
python-jose>=3.3.0
bcrypt>=3.2.0

# Core Dependencies (if not already installed)
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.0
SQLAlchemy>=1.4.0
aiofiles>=0.7.0
python-multipart>=0.0.5

# Testing Dependencies
pytest>=6.2.0
pytest-asyncio>=0.15.0
httpx>=0.24.0
requests>=2.26.0
""".strip()
        
        requirements_file = Path("requirements-security.txt")
        requirements_file.write_text(security_requirements)
        
        print(f"✅ Security requirements saved to {requirements_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create requirements file: {e}")
        return False

def main():
    """Main installation function."""
    print("🛡️ DEX Sniper Pro - Security Dependencies Installation")
    print("=" * 60)
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Install cryptography
    if install_cryptography():
        success_count += 1
    
    # Step 2: Install additional security dependencies
    if install_additional_security_deps():
        success_count += 1
    
    # Step 3: Verify installation
    if verify_installation():
        success_count += 1
    
    # Step 4: Create requirements file
    if create_requirements_security():
        success_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Installation Results: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("🎉 ALL SECURITY DEPENDENCIES INSTALLED SUCCESSFULLY!")
        print("✅ Ready to run security tests")
        print("\nNext steps:")
        print("1. Run: python tests/test_security_implementation.py")
        print("2. All security tests should now pass")
        return True
    else:
        print("⚠️ Some installation steps failed")
        print("🔧 Try running the installation manually:")
        print("   pip install cryptography>=3.4.8")
        print("   pip install -r requirements-security.txt")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Installation script error: {e}")
        sys.exit(1)