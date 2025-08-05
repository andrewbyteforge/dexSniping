"""
Apply Dashboard Fix Script
File: apply_dashboard_fix.py

Fixes the specific issue in your dashboard template where
data.success_rate.toFixed(1) fails because success_rate is already a string.
"""

import os
from pathlib import Path

def fix_dashboard():
    """Apply the dashboard fix."""
    
    # Find your dashboard file
    dashboard_files = [
        "frontend/templates/pages/dashboard.html",
        "templates/dashboard.html",
        "app/templates/dashboard.html"
    ]
    
    dashboard_path = None
    for file_path in dashboard_files:
        if Path(file_path).exists():
            dashboard_path = Path(file_path)
            break
    
    if not dashboard_path:
        print("❌ Could not find dashboard.html file")
        return False
    
    print(f"✅ Found dashboard at: {dashboard_path}")
    
    try:
        # Read the current content
        content = dashboard_path.read_text(encoding='utf-8')
        
        # Create backup
        backup_path = dashboard_path.with_suffix('.html.backup')
        backup_path.write_text(content, encoding='utf-8')
        print(f"✅ Created backup: {backup_path}")
        
        # Replace the problematic lines
        old_success_line = "successElement.textContent = data.success_rate.toFixed(1) + '%';"
        new_success_line = "successElement.textContent = safeFormat(data.success_rate, 'percentage');"
        
        old_quick_line = "quickSuccessElement.textContent = data.success_rate.toFixed(1) + '%';"
        new_quick_line = "quickSuccessElement.textContent = safeFormat(data.success_rate, 'percentage');"
        
        # Apply fixes
        content = content.replace(old_success_line, new_success_line)
        content = content.replace(old_quick_line, new_quick_line)
        
        # Add the helper function at the start of updateDashboardStats
        old_function_start = "function updateDashboardStats(data) {\n        try {"
        new_function_start = """function updateDashboardStats(data) {
        try {
            console.log('📊 Updating dashboard stats with:', data);
            
            // Helper function to safely format values
            function safeFormat(value, type = 'number') {
                if (value === null || value === undefined) return '0';
                
                switch (type) {
                    case 'currency':
                        if (typeof value === 'string' && value.includes('$')) return value;
                        return formatCurrency(parseFloat(value) || 0);
                    
                    case 'percentage':
                        if (typeof value === 'string' && value.includes('%')) return value;
                        return (parseFloat(value) || 0).toFixed(1) + '%';
                    
                    case 'number':
                        if (typeof value === 'string') return value;
                        return (parseFloat(value) || 0).toString();
                    
                    default:
                        return value.toString();
                }
            }"""
        
        content = content.replace(old_function_start, new_function_start)
        
        # Also fix the active trades mapping
        old_trades_line = "tradesElement.textContent = data.trades_today;"
        new_trades_line = "tradesElement.textContent = data.active_trades || data.trades_today || 0;"
        content = content.replace(old_trades_line, new_trades_line)
        
        # Fix uptime mapping
        old_uptime_line = "uptimeElement.textContent = data.uptime_percent.toFixed(1) + '%';"
        new_uptime_line = "uptimeElement.textContent = data.system_uptime || '0 hours';"
        content = content.replace(old_uptime_line, new_uptime_line)
        
        # Write the fixed content back
        dashboard_path.write_text(content, encoding='utf-8')
        
        print("✅ Applied dashboard fixes successfully!")
        print("\nNext steps:")
        print("1. Restart your server: uvicorn app.main:app --reload")  
        print("2. Refresh dashboard: http://127.0.0.1:8000/dashboard")
        print("3. Check browser console for: '✅ Dashboard stats updated successfully'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

if __name__ == "__main__":
    print("Dashboard Data Display Fix")
    print("=" * 30)
    fix_dashboard()