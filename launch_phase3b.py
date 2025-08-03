"""
Phase 3B Launch Script
File: launch_phase3b.py

Complete launcher for Phase 3B development including:
- Setup verification
- Dashboard initialization
- Server launch with proper configuration
- Browser opening
- Development mode configuration

Usage: python launch_phase3b.py
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def print_header():
    """Print the Phase 3B launch header."""
    print("🚀 DEX SNIPING PLATFORM - PHASE 3B LAUNCHER")
    print("=" * 60)
    print("Professional Trading Dashboard with Bootstrap 5")
    print("Real-time WebSocket feeds and live data integration")
    print("=" * 60)


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("\n🔍 Checking prerequisites...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        issues.append("Python 3.9+ required")
    else:
        print("   ✅ Python version: OK")
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Virtual environment: Active")
    else:
        issues.append("Virtual environment not activated")
    
    # Check key files
    required_files = [
        "app/main.py",
        "app/api/v1/endpoints/tokens.py",
        "app/config.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}: Found")
        else:
            issues.append(f"Missing file: {file_path}")
    
    # Check if Phase 3A is complete
    try:
        from app.core.dex.dex_manager import DEXManager
        from app.core.dex.uniswap_integration import UniswapV2Integration
        print("   ✅ Phase 3A DEX integration: Available")
    except ImportError as e:
        issues.append(f"Phase 3A components missing: {e}")
    
    return issues


def setup_dashboard():
    """Set up the dashboard if not already done."""
    print("\n🏗️ Setting up Phase 3B dashboard...")
    
    # Check if dashboard exists
    if os.path.exists("dashboard/index.html"):
        print("   ✅ Dashboard already set up")
        return True
    
    # Run setup script
    try:
        print("   🔄 Running dashboard setup...")
        result = subprocess.run([sys.executable, "setup_phase3b_dashboard.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ Dashboard setup completed")
            return True
        else:
            print(f"   ❌ Dashboard setup failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Dashboard setup timed out")
        return False
    except FileNotFoundError:
        print("   ⚠️ Setup script not found, creating basic dashboard...")
        return create_basic_dashboard()


def create_basic_dashboard():
    """Create a basic dashboard if setup script is not available."""
    try:
        os.makedirs("dashboard", exist_ok=True)
        
        basic_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEX Sniping Platform - Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card shadow">
                    <div class="card-body text-center">
                        <h1 class="card-title text-primary">
                            <i class="bi bi-graph-up-arrow"></i>
                            DEX Sniping Dashboard
                        </h1>
                        <p class="card-text lead">Phase 3B Professional Trading Interface</p>
                        
                        <div class="row mt-4">
                            <div class="col-md-4">
                                <div class="card bg-primary text-white">
                                    <div class="card-body">
                                        <h5><i class="bi bi-lightning"></i> Block 0 Sniping</h5>
                                        <p>Ready for instant execution</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-success text-white">
                                    <div class="card-body">
                                        <h5><i class="bi bi-search"></i> Token Discovery</h5>
                                        <p>Live monitoring active</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-info text-white">
                                    <div class="card-body">
                                        <h5><i class="bi bi-shield"></i> Risk Assessment</h5>
                                        <p>AI analysis ready</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <a href="/docs" class="btn btn-primary me-2">
                                <i class="bi bi-book"></i> API Documentation
                            </a>
                            <a href="/api/v1/health" class="btn btn-outline-success">
                                <i class="bi bi-heart-pulse"></i> System Health
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/js/bootstrap.bundle.min.js"></script>
    <script>
        // Test API connectivity
        fetch('/api/v1/health')
            .then(response => response.json())
            .then(data => console.log('API Health:', data))
            .catch(error => console.error('API Error:', error));
    </script>
</body>
</html>"""
        
        with open("dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(basic_html)
        
        print("   ✅ Basic dashboard created")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create basic dashboard: {e}")
        return False


def install_dependencies():
    """Install any missing dependencies."""
    print("\n📦 Checking dependencies...")
    
    try:
        # Check if uvicorn is available
        import uvicorn
        print("   ✅ uvicorn: Available")
    except ImportError:
        print("   🔄 Installing uvicorn...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn[standard]"])
    
    # Install from requirements if available
    if os.path.exists("requirements.txt"):
        print("   🔄 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("   ✅ Requirements installed")
    
    return True


def launch_server():
    """Launch the FastAPI server."""
    print("\n🚀 Launching FastAPI server...")
    
    try:
        # Change to project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start server
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8001",
            "--reload",
            "--log-level", "info"
        ]
        
        print("   🔄 Starting server on http://127.0.0.1:8001")
        print("   📊 Dashboard will be available at http://127.0.0.1:8001/dashboard")
        print("   📚 API docs available at http://127.0.0.1:8001/docs")
        print("\n   Press Ctrl+C to stop the server")
        
        # Open browser after a short delay
        import threading
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://127.0.0.1:8001")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start server (this will block)
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
        return False
    
    return True


def show_development_info():
    """Show information for Phase 3B development."""
    print("\n📋 PHASE 3B DEVELOPMENT INFO")
    print("-" * 40)
    
    print("\n🎯 Current Status:")
    print("   ✅ Phase 3A: Complete (96.4% validation)")
    print("   🔄 Phase 3B: Dashboard foundation ready")
    print("   📊 Bootstrap 5: Professional UI framework")
    print("   🔗 WebSocket: Real-time data feeds")
    
    print("\n🛠️ Development URLs:")
    print("   🏠 Home: http://127.0.0.1:8001")
    print("   📊 Dashboard: http://127.0.0.1:8001/dashboard")
    print("   📚 API Docs: http://127.0.0.1:8001/docs")
    print("   💓 Health: http://127.0.0.1:8001/health")
    
    print("\n🔧 API Endpoints:")
    print("   📈 Stats: GET /api/v1/dashboard/stats")
    print("   🪙 Tokens: GET /api/v1/dashboard/live-tokens")
    print("   🚨 Alerts: GET /api/v1/dashboard/alerts")
    print("   📊 Portfolio: GET /api/v1/dashboard/portfolio")
    print("   🔗 WebSocket: WS /api/v1/dashboard/ws")
    
    print("\n🎨 Frontend Features:")
    print("   • Bootstrap 5.3 responsive design")
    print("   • Real-time WebSocket updates")
    print("   • Chart.js for data visualization")
    print("   • Professional trading interface")
    print("   • Mobile-responsive layout")


def main():
    """Main launcher function."""
    print_header()
    
    # Check prerequisites
    issues = check_prerequisites()
    if issues:
        print("\n❌ Prerequisites not met:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n🔧 Please resolve these issues and try again.")
        return False
    
    print("   ✅ All prerequisites met")
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return False
    
    # Setup dashboard
    if not setup_dashboard():
        print("\n❌ Failed to set up dashboard")
        return False
    
    # Show development info
    show_development_info()
    
    # Ask user if they want to launch
    print("\n🚀 Ready to launch Phase 3B dashboard!")
    response = input("Launch server now? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        return launch_server()
    else:
        print("\n📝 To launch manually:")
        print("   uvicorn app.main:app --reload --port 8001")
        print("   Then open: http://127.0.0.1:8001/dashboard")
        return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Phase 3B launch completed!")
        else:
            print("\n❌ Launch encountered issues.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Launch cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)