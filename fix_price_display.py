"""
Quick Fix for Price Display Error
File: fix_price_display.py

Fixes the price.toFixed() error by adding proper type checking.
"""

import os
from pathlib import Path

def fix_price_display():
    """Fix the price display error in dashboard."""
    
    # Find dashboard file
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
        # Read current content
        content = dashboard_path.read_text(encoding='utf-8')
        
        # Fix the price display line
        old_price_line = "html += '        <small class=\"text-muted\">$' + (price ? price.toFixed(6) : '0.00') + '</small>';"
        new_price_line = "html += '        <small class=\"text-muted\">$' + formatPrice(price) + '</small>';"
        
        if old_price_line in content:
            content = content.replace(old_price_line, new_price_line)
            print("✅ Fixed price display line")
        
        # Fix the price change line
        old_change_line = "html += '        ' + (isPositive ? '+' : '') + (priceChange ? priceChange.toFixed(2) : '0.00') + '%';"
        new_change_line = "html += '        ' + (isPositive ? '+' : '') + formatPrice(priceChange, 2) + '%';"
        
        if old_change_line in content:
            content = content.replace(old_change_line, new_change_line)
            print("✅ Fixed price change line")
        
        # Fix the risk score line
        old_risk_line = "html += '        Risk: <span class=\"badge bg-secondary\">' + (riskScore ? riskScore.toFixed(1) : '0.0') + '</span>';"
        new_risk_line = "html += '        Risk: <span class=\"badge bg-secondary\">' + formatPrice(riskScore, 1) + '</span>';"
        
        if old_risk_line in content:
            content = content.replace(old_risk_line, new_risk_line)
            print("✅ Fixed risk score line")
        
        # Add the formatPrice helper function before the displayTokens function
        display_tokens_pos = content.find("function displayTokens(tokens) {")
        if display_tokens_pos != -1:
            format_price_function = '''    function formatPrice(value, decimals) {
        decimals = decimals || 6;
        if (value === null || value === undefined) return '0.00';
        const num = parseFloat(value);
        if (isNaN(num)) return '0.00';
        return num.toFixed(decimals);
    }
    
    '''
            content = content[:display_tokens_pos] + format_price_function + content[display_tokens_pos:]
            print("✅ Added formatPrice helper function")
        
        # Write the updated content back
        dashboard_path.write_text(content, encoding='utf-8')
        
        print("✅ Fixed price display errors!")
        print("\nNext steps:")
        print("1. Restart server: uvicorn app.main:app --reload")
        print("2. Refresh dashboard: http://127.0.0.1:8000/dashboard")
        print("3. Tokens should now display properly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing price display: {e}")
        return False

if __name__ == "__main__":
    print("Fix Price Display Error")
    print("=" * 25)
    fix_price_display()