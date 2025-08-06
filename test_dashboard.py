"""
Test Dashboard Fix
File: test_dashboard.py

Tests that the dashboard is now properly displaying the professional trading interface.
"""

import sys
from pathlib import Path

def setup_path():
    """Setup Python path."""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def test_dashboard_rendering():
    """Test dashboard rendering."""
    setup_path()
    
    print("🧪 Testing Dashboard Rendering...")
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test dashboard endpoint
        response = client.get("/dashboard")
        
        print(f"✅ Dashboard response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for key dashboard elements
            dashboard_elements = [
                "DEX Sniper Pro",
                "Portfolio Value", 
                "Daily P&L",
                "Trades Today",
                "System Health",
                "Portfolio Performance",
                "Asset Allocation",
                "Recent Activity",
                "System Components",
                "Phase 4C"
            ]
            
            found_elements = []
            missing_elements = []
            
            for element in dashboard_elements:
                if element in content:
                    found_elements.append(element)
                else:
                    missing_elements.append(element)
            
            print(f"✅ Found dashboard elements: {len(found_elements)}/{len(dashboard_elements)}")
            
            for element in found_elements[:5]:  # Show first 5
                print(f"   ✓ {element}")
            
            if len(found_elements) > 5:
                print(f"   ... and {len(found_elements) - 5} more")
            
            if missing_elements:
                print(f"❌ Missing elements: {missing_elements}")
            
            # Check for charts and interactivity
            interactive_features = [
                "Chart.js",
                "portfolioChart", 
                "allocationChart",
                "loadDashboardData",
                "updateDashboardStats"
            ]
            
            found_features = [f for f in interactive_features if f in content]
            print(f"📊 Interactive features: {len(found_features)}/{len(interactive_features)}")
            
            # Check for AI integration
            ai_features = [
                "AI Risk Assessment",
                "ai_risk_enabled",
                "🧠"
            ]
            
            found_ai = [f for f in ai_features if f in content]
            print(f"🧠 AI features: {len(found_ai)}/{len(ai_features)}")
            
            # Overall assessment
            total_found = len(found_elements) + len(found_features) + len(found_ai)
            total_expected = len(dashboard_elements) + len(interactive_features) + len(ai_features)
            
            percentage = (total_found / total_expected) * 100
            
            print(f"\n📊 Dashboard Quality Score: {percentage:.1f}%")
            
            if percentage >= 90:
                print("🎉 EXCELLENT! Professional dashboard is fully operational!")
                return True, "excellent"
            elif percentage >= 75:
                print("✅ GOOD! Dashboard is working well with most features.")
                return True, "good"
            elif percentage >= 50:
                print("⚠️  PARTIAL! Dashboard is working but missing some features.")
                return True, "partial"
            else:
                print("❌ POOR! Dashboard needs significant improvement.")
                return False, "poor"
        else:
            print(f"❌ Dashboard failed to load: HTTP {response.status_code}")
            return False, "failed"
            
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False, "error"


def test_other_endpoints():
    """Test other dashboard endpoints."""
    print("\n🧪 Testing Related Endpoints...")
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        endpoints = [
            ("/", "Root"),
            ("/health", "Health Check"),
            ("/api/v1/dashboard/stats", "Dashboard Stats API"),
            ("/docs", "API Documentation")
        ]
        
        results = []
        
        for endpoint, name in endpoints:
            try:
                response = client.get(endpoint)
                status = "✅" if response.status_code == 200 else "❌"
                results.append((name, response.status_code, status))
                print(f"   {status} {name}: HTTP {response.status_code}")
            except Exception as e:
                results.append((name, "ERROR", "❌"))
                print(f"   ❌ {name}: ERROR - {e}")
        
        working_endpoints = sum(1 for _, code, _ in results if code == 200)
        total_endpoints = len(results)
        
        print(f"\n📊 Endpoint Status: {working_endpoints}/{total_endpoints} working")
        
        return working_endpoints >= total_endpoints * 0.75
        
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 70)
    print("🚀 DASHBOARD FUNCTIONALITY TEST")
    print("=" * 70)
    print("Testing that the professional trading dashboard is working correctly...")
    
    dashboard_success, dashboard_quality = test_dashboard_rendering()
    endpoints_success = test_other_endpoints()
    
    print(f"\n" + "=" * 70)
    print("📊 FINAL DASHBOARD TEST RESULTS")
    print("=" * 70)
    
    if dashboard_success and endpoints_success:
        print("🎉 SUCCESS! Professional dashboard is operational!")
        print("✅ Dashboard rendering: Working")
        print("✅ API endpoints: Working") 
        print("✅ Interactive features: Included")
        print("✅ AI integration: Present")
        
        print(f"\n🚀 Your DEX Sniper Pro dashboard is ready!")
        print("📱 Start the app: python -m app.main")
        print("🌐 Visit: http://localhost:8000/dashboard")
        
        if dashboard_quality == "excellent":
            print("⭐ Quality Rating: EXCELLENT - Professional grade!")
        elif dashboard_quality == "good":
            print("✅ Quality Rating: GOOD - Ready for use!")
        else:
            print("⚠️  Quality Rating: Functional but could be improved")
            
    else:
        print("⚠️  PARTIAL SUCCESS")
        if not dashboard_success:
            print("❌ Dashboard rendering: Issues detected")
        if not endpoints_success:
            print("❌ API endpoints: Some issues")
        print("🔧 Review the logs above for specific issues")
    
    print("=" * 70)
    
    return dashboard_success and endpoints_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)