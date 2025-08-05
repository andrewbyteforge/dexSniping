"""
Add Wallet Router to Existing App
File: add_wallet_router.py

This script will add the wallet router to your existing main.py application.
Run this once to patch your current application.
"""

import sys
from pathlib import Path

def patch_main_py():
    """Add wallet router to the existing main.py file."""
    print("🔧 Patching main.py to include wallet router...")
    
    main_py_path = Path("app/main.py")
    
    if not main_py_path.exists():
        print("❌ app/main.py not found!")
        return False
    
    # Read current main.py content
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Current main.py loaded")
        
        # Check if wallet router is already imported
        if "from app.api.v1.endpoints.wallet import router as wallet_router" in content:
            print("✅ Wallet router import already exists")
        else:
            # Add wallet router import after other imports
            import_line = "from app.api.v1.endpoints.wallet import router as wallet_router"
            
            # Find a good place to add the import (after FastAPI imports)
            if "from fastapi import FastAPI" in content:
                content = content.replace(
                    "from fastapi import FastAPI",
                    f"from fastapi import FastAPI\nfrom app.api.v1.endpoints.wallet import router as wallet_router"
                )
                print("✅ Added wallet router import")
            elif "import FastAPI" in content:
                content = content.replace(
                    "import FastAPI",
                    f"import FastAPI\nfrom app.api.v1.endpoints.wallet import router as wallet_router"
                )
                print("✅ Added wallet router import")
            else:
                # Add at the end of imports section
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        import_end = i
                
                lines.insert(import_end + 1, import_line)
                content = '\n'.join(lines)
                print("✅ Added wallet router import")
        
        # Check if wallet router is included in the app
        if "app.include_router(wallet_router" in content:
            print("✅ Wallet router inclusion already exists")
        else:
            # Add wallet router inclusion
            # Look for existing router inclusions or app creation
            if "app = FastAPI(" in content or "app = create_application(" in content:
                # Find the app creation and add router inclusion after it
                lines = content.split('\n')
                app_creation_line = -1
                
                for i, line in enumerate(lines):
                    if "app = FastAPI(" in line or "app = create_application(" in line:
                        app_creation_line = i
                        break
                
                if app_creation_line != -1:
                    # Find the end of the app creation (look for closing parenthesis)
                    insertion_point = app_creation_line + 1
                    paren_count = 0
                    in_app_creation = False
                    
                    for i in range(app_creation_line, len(lines)):
                        line = lines[i]
                        if "app = " in line:
                            in_app_creation = True
                        
                        if in_app_creation:
                            paren_count += line.count('(') - line.count(')')
                            if paren_count <= 0 and ')' in line:
                                insertion_point = i + 1
                                break
                    
                    # Insert wallet router inclusion
                    router_inclusion = """
# Include Phase 4B Wallet API Router
try:
    app.include_router(wallet_router, prefix="/api/v1")
    print("✅ Wallet API router included successfully")
except Exception as e:
    print(f"❌ Failed to include wallet router: {e}")
"""
                    lines.insert(insertion_point, router_inclusion)
                    content = '\n'.join(lines)
                    print("✅ Added wallet router inclusion")
                else:
                    print("⚠️ Could not find app creation line")
            else:
                print("⚠️ Could not find where to add router inclusion")
        
        # Write the updated content back
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ main.py patched successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error patching main.py: {e}")
        return False

def create_simple_main_py():
    """Create a simple main.py that definitely includes the wallet router."""
    print("🔧 Creating simple main.py with wallet router...")
    
    simple_main_content = '''"""
Simple Main Application with Wallet Router
File: app/main.py

Simplified version that definitely includes the wallet API.
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import wallet router
from app.api.v1.endpoints.wallet import router as wallet_router

# Create FastAPI app
app = FastAPI(
    title="DEX Sniper Pro - Phase 4B",
    description="Professional trading bot with wallet integration",
    version="4.0.0-beta",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include wallet router
app.include_router(wallet_router, prefix="/api/v1")

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "DEX Sniper Pro - Phase 4B",
        "version": "4.0.0-beta",
        "wallet_api": "Available at /api/v1/wallet/",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "DEX Sniper Pro Phase 4B",
        "wallet_api": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
'''
    
    try:
        # Backup existing main.py
        main_py_path = Path("app/main.py")
        if main_py_path.exists():
            backup_path = Path("app/main.py.backup")
            with open(main_py_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f"✅ Backed up existing main.py to {backup_path}")
        
        # Write simple main.py
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(simple_main_content)
        
        print("✅ Created simple main.py with wallet router")
        return True
        
    except Exception as e:
        print(f"❌ Error creating simple main.py: {e}")
        return False

def main():
    """Main function."""
    print("🔧 DEX Sniper Pro - Add Wallet Router Fix")
    print("=" * 50)
    
    choice = input("Choose option:\n1. Patch existing main.py\n2. Create simple main.py\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        success = patch_main_py()
    elif choice == "2":
        success = create_simple_main_py()
    else:
        print("❌ Invalid choice")
        return False
    
    if success:
        print("\n✅ Fix applied successfully!")
        print("🚀 Now restart the server:")
        print("   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
        print("\n🧪 Then test the wallet API:")
        print("   curl http://127.0.0.1:8000/api/v1/wallet/health")
        return True
    else:
        print("\n❌ Fix failed - check error messages above")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Fix interrupted by user")
    except Exception as e:
        print(f"\n💥 Fix error: {e}")
