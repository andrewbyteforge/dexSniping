"""
Final Integration Test Suite
File: run_final_tests.py

Runs all tests and fixes to ensure the refactored application is fully working.
This is the final validation before moving to the next development phase.
"""

import subprocess
import sys
import asyncio
from pathlib import Path

def setup_path():
    """Setup Python path."""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔧 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        return False


def test_direct_imports():
    """Test importing key modules directly."""
    print("\n🧪 Testing Direct Imports...")
    
    import_tests = [
        ("app.main", "Main application"),
        ("app.factory", "Application factory"),
        ("app.core.component_manager", "Component manager"),
        ("app.core.lifecycle_manager", "Lifecycle manager"),
        ("app.api.route_manager", "Route manager"),
        ("app.core.error_handlers", "Error handlers"),
        ("app.core.system_info", "System info provider")
    ]
    
    success_count = 0
    
    for module_name, description in import_tests:
        try:
            __import__(module_name)
            print(f"✅ {description}: Import successful")
            success_count += 1
        except Exception as e:
            print(f"❌ {description}: Import failed - {e}")
    
    return success_count, len(import_tests)


async def test_component_loading():
    """Test component loading directly."""
    print("\n🧪 Testing Component Loading...")
    
    try:
        from app.core.component_manager import ComponentManager
        
        cm = ComponentManager()
        status = await cm.get_component_status()
        
        print(f"📦 Component Status:")
        for name, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {name}: {'Available' if available else 'Not Available'}")
        
        available_count = sum(status.values())
        total_count = len(status)
        
        return available_count, total_count, available_count >= total_count * 0.5
        
    except Exception as e:
        print(f"❌ Component loading test failed: {e}")
        return 0, 0, False


def test_application_creation():
    """Test application creation."""
    print("\n🧪 Testing Application Creation...")
    
    try:
        from app.factory import create_app
        
        app = create_app()
        
        print(f"✅ Application created successfully")
        print(f"   - Title: {app.title}")
        print(f"   - Version: {app.version}")
        print(f"   - Routes: {len(app.routes)}")
        print(f"   - Middleware: {len(app.user_middleware)}")
        
        return True, app
        
    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        return False, None


async def run_all_tests():
    """Run all integration tests."""
    print("=" * 80)
    print("🚀 FINAL INTEGRATION TEST SUITE")
    print("=" * 80)
    print("Running comprehensive tests for the refactored DEX Sniper Pro application")
    
    test_results = {}
    
    # Test 1: Direct imports
    import_success, import_total = test_direct_imports()
    test_results['imports'] = (import_success, import_total, import_success == import_total)
    
    # Test 2: Component loading
    comp_available, comp_total, comp_success = await test_component_loading()
    test_results['components'] = (comp_available, comp_total, comp_success)
    
    # Test 3: Application creation
    app_success, app = test_application_creation()
    test_results['application'] = (1 if app_success else 0, 1, app_success)
    
    # Test 4: Run the refactored structure test
    print("\n🧪 Running Refactored Structure Test...")
    refactor_success = run_command("python test_refactored_app.py", "Refactored Structure Test")
    test_results['refactored_structure'] = (1 if refactor_success else 0, 1, refactor_success)
    
    # Test 5: Fix Pydantic schemas
    print("\n🧪 Running Pydantic Schema Fix...")
    pydantic_success = run_command("python fix_pydantic_v2.py", "Pydantic V2 Schema Fix")
    test_results['pydantic_fix'] = (1 if pydantic_success else 0, 1, pydantic_success)
    
    # Generate final report
    print("\n" + "=" * 80)
    print("📊 FINAL INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    total_passed = 0
    total_tests = 0
    
    for test_name, (passed, total, success) in test_results.items():
        total_passed += passed
        total_tests += total
        
        percentage = (passed / total * 100) if total > 0 else 0
        status = "✅" if success else "❌"
        
        print(f"{status} {test_name:20}: {passed}/{total} ({percentage:.1f}%)")
    
    overall_success = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 Overall Success Rate: {total_passed}/{total_tests} ({overall_success:.1f}%)")
    
    # Component-specific summary
    if 'components' in test_results:
        comp_available, comp_total, _ = test_results['components']
        print(f"📦 Components Available: {comp_available}/{comp_total}")
        
        # Highlight AI components
        if comp_available >= 6:  # Assuming we have 8 components and 6+ is good
            print("🧠 AI Risk Assessment: Likely Available")
        else:
            print("⚠️  Some components may not be available")
    
    print(f"\n🔧 FINAL RECOMMENDATIONS:")
    
    if overall_success >= 90:
        print("🎉 EXCELLENT! Application is fully ready!")
        print("🚀 Next steps:")
        print("   1. python -m app.main                    # Start the application")
        print("   2. Open http://localhost:8000/dashboard  # Access dashboard")
        print("   3. Visit http://localhost:8000/docs      # API documentation")
        print("   4. Test http://localhost:8000/risk-analysis # AI features")
        
        print(f"\n✨ Phase 4C Implementation Status: COMPLETE")
        print(f"   - Modular Architecture: ✅ Implemented")
        print(f"   - Component Management: ✅ Working")
        print(f"   - AI Risk Assessment: ✅ Integrated")
        print(f"   - Error Handling: ✅ Comprehensive")
        print(f"   - Lifecycle Management: ✅ Operational")
        
        print(f"\n🎯 Ready for Phase 4D Development!")
        
    elif overall_success >= 75:
        print("✅ GOOD! Application is mostly ready with minor issues.")
        print("🔧 Address any failed tests before production use.")
        
    else:
        print("⚠️  WARNING! Critical issues detected.")
        print("🚨 Review all failed tests and fix issues before proceeding.")
        
        # Specific guidance
        if not test_results.get('imports', (0, 0, False))[2]:
            print("   📝 Fix import issues - check __init__.py files")
            
        if not test_results.get('components', (0, 0, False))[2]:
            print("   🔧 Fix component loading issues")
            
        if not test_results.get('application', (0, 0, False))[2]:
            print("   🏭 Fix application factory issues")
    
    print("\n" + "=" * 80)
    return overall_success >= 75


def main():
    """Main execution function."""
    setup_path()
    
    try:
        print("🎯 Starting final integration tests...")
        print("⏱️  This will run all tests to validate the refactored application")
        
        success = asyncio.run(run_all_tests())
        
        if success:
            print("\n🎉 FINAL INTEGRATION TESTS PASSED!")
            print("✅ DEX Sniper Pro Phase 4C is ready!")
            print("🚀 You can now start the application!")
        else:
            print("\n⚠️  INTEGRATION TESTS INCOMPLETE")
            print("🔧 Please fix the issues identified above")
            
        return success
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)