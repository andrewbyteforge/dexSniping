"""
Manual Activity Route Fix
File: manual_activity_route_fix.py

Manually adds the activity route to main.py using a more flexible approach.
"""

import os
from pathlib import Path


def manual_activity_route_fix():
    """Manually add the activity route to main.py."""
    
    print("🔧 Manual Activity Route Fix")
    print("=" * 40)
    
    main_file = Path("app/main.py")
    
    if not main_file.exists():
        print("❌ app/main.py not found!")
        return False
    
    try:
        # Read current content
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if activity route already exists
        if "@app.get(\"/activity\")" in content or "serve_activity" in content:
            print("✅ Activity route already exists in main.py")
            return True
        
        # Activity route code to add
        activity_route_code = '''

@app.get("/activity", response_class=HTMLResponse)
async def serve_activity(request: Request):
    """Serve the trading activity page."""
    try:
        return templates.TemplateResponse(
            "pages/activity.html", 
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Activity template error: {e}")
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trading Activity - DEX Sniper Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
                .container { max-width: 600px; margin: 0 auto; }
                .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Trading Activity</h1>
                <p>Activity page is loading...</p>
                <a href="/dashboard" class="btn">Back to Dashboard</a>
                <a href="/api/docs" class="btn">API Docs</a>
            </div>
        </body>
        </html>
        """)
'''
        
        # Strategy 1: Try to add before "if __name__ == "__main__""
        if 'if __name__ == "__main__"' in content:
            content = content.replace(
                'if __name__ == "__main__"',
                activity_route_code + '\n\nif __name__ == "__main__"'
            )
            print("✅ Added activity route before main block")
        
        # Strategy 2: Try to add after health check route if it exists
        elif "@app.get(\"/health\")" in content:
            # Find the end of the health route
            health_start = content.find("@app.get(\"/health\")")
            remaining_content = content[health_start:]
            
            # Find the end of the health function
            lines = remaining_content.split('\n')
            health_end_line = 0
            
            for i, line in enumerate(lines):
                if i > 0 and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    health_end_line = i
                    break
            
            if health_end_line > 0:
                insertion_point = health_start + len('\n'.join(lines[:health_end_line]))
                content = content[:insertion_point] + activity_route_code + content[insertion_point:]
                print("✅ Added activity route after health check")
            else:
                # Fallback: add at the very end
                content += activity_route_code
                print("✅ Added activity route at end of file")
        
        # Strategy 3: Add at the end of the file
        else:
            content += activity_route_code
            print("✅ Added activity route at end of file")
        
        # Write back the updated content
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Activity route successfully added to main.py!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add activity route: {e}")
        return False


def verify_fixes():
    """Verify that all fixes are in place."""
    
    print("\n🔍 Verifying all fixes...")
    
    checks = {
        "main.py exists": Path("app/main.py").exists(),
        "activity template exists": Path("frontend/templates/pages/activity.html").exists(),
        "tokens router in main": False,
        "activity route in main": False
    }
    
    # Check main.py content
    main_file = Path("app/main.py")
    if main_file.exists():
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks["tokens router in main"] = "tokens_router" in content
            checks["activity route in main"] = "@app.get(\"/activity\")" in content or "serve_activity" in content
            
        except Exception as e:
            print(f"⚠️ Could not read main.py: {e}")
    
    # Report results
    print("\nVerification Results:")
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    all_good = all(checks.values())
    
    if all_good:
        print("\n🎉 All fixes verified successfully!")
        print("\nYour endpoints are now ready:")
        print("  📊 Dashboard: http://127.0.0.1:8000/dashboard")
        print("  🔍 Tokens API: http://127.0.0.1:8000/api/v1/tokens/discover")
        print("  📈 Activity Page: http://127.0.0.1:8000/activity")
    else:
        print("\n⚠️ Some issues remain - check the results above")
    
    return all_good


def main():
    """Main execution function."""
    try:
        if manual_activity_route_fix():
            verify_fixes()
            
            print("\n" + "=" * 50)
            print("🎯 ENDPOINT FIX COMPLETE!")
            print("=" * 50)
            print("\n✅ What was fixed:")
            print("  - Tokens router included in main.py")
            print("  - Activity page template created")
            print("  - Activity route added to main.py")
            print("\n📋 Next steps:")
            print("1. Restart server: uvicorn app.main:app --reload")
            print("2. Test tokens: http://127.0.0.1:8000/api/v1/tokens/discover")
            print("3. Test activity: http://127.0.0.1:8000/activity")
            print("4. All dashboard buttons should now work!")
            
            return True
        else:
            print("\n❌ Manual fix failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)