"""
Fix Token Loading Script
File: fix_token_loading.py

Fixes the token loading issue in the dashboard by updating the JavaScript
to handle the actual API response format correctly.
"""

import os
from pathlib import Path

def fix_token_loading():
    """Fix the token loading in dashboard."""
    
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
        
        # Create backup
        backup_path = dashboard_path.with_suffix('.html.tokens_backup')
        backup_path.write_text(content, encoding='utf-8')
        print(f"✅ Created backup: {backup_path}")
        
        # Find the loadTokens function and replace it
        old_load_tokens_start = "async function loadTokens() {"
        old_load_tokens_end = "    }\n    \n    function displayTokens("
        
        new_load_tokens = '''async function loadTokens() {
        try {
            console.log('🔍 Loading tokens...');
            
            const response = await fetch('/api/v1/tokens/discover?limit=10&offset=0&sort=age&order=desc');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('✅ Raw tokens API response:', data);
            
            // Handle different possible response formats
            let tokens = [];
            
            if (data.discovered_tokens && Array.isArray(data.discovered_tokens)) {
                tokens = data.discovered_tokens;
                console.log('✅ Using discovered_tokens array');
            } else if (data.tokens && Array.isArray(data.tokens)) {
                tokens = data.tokens;
                console.log('✅ Using tokens array');
            } else if (Array.isArray(data)) {
                tokens = data;
                console.log('✅ Using direct array');
            } else {
                console.warn('⚠️ No token array found in response');
                console.log('Available keys:', Object.keys(data));
            }
            
            console.log(`📋 Processing ${tokens.length} tokens`);
            
            if (tokens.length > 0) {
                tokensData = tokens;
                displayTokens(tokens);
                
                // Update tokens scanned count
                const scannedElement = document.getElementById('tokensScanned');
                if (scannedElement) {
                    scannedElement.textContent = data.total_discovered || tokens.length;
                }
            } else {
                displayNoTokens();
            }
            
        } catch (error) {
            console.error('❌ Failed to load tokens:', error);
            displayTokensError(error.message);
        }
    }
    
    function displayNoTokens() {
        const container = document.getElementById('tokensList');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-search fs-2 mb-3"></i>
                    <p class="mb-2">No tokens discovered yet</p>
                    <small>Token scanning is active...</small>
                </div>
            `;
        }
    }
    
    function displayTokensError(errorMessage) {
        const container = document.getElementById('tokensList');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i>
                    <strong>Unable to load tokens</strong>
                    <br><small>Error: ${errorMessage}</small>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="loadTokens()">
                            <i class="bi bi-arrow-clockwise"></i> Retry
                        </button>
                    </div>
                </div>
            `;
        }
    }
    
    function displayTokens('''
        
        # Replace the old loadTokens function
        start_pos = content.find(old_load_tokens_start)
        end_pos = content.find(old_load_tokens_end)
        
        if start_pos != -1 and end_pos != -1:
            # Replace the function
            content = content[:start_pos] + new_load_tokens + content[end_pos:]
            print("✅ Replaced loadTokens function")
        else:
            print("⚠️ Could not find loadTokens function to replace")
            # Add the new function before the displayTokens function
            display_tokens_pos = content.find("function displayTokens(")
            if display_tokens_pos != -1:
                content = content[:display_tokens_pos] + new_load_tokens + "\n    " + content[display_tokens_pos:]
                print("✅ Added enhanced loadTokens function")
        
        # Also enhance the displayTokens function to handle different data formats
        old_display_start = "function displayTokens(tokens) {"
        new_display_tokens = '''function displayTokens(tokens) {
        const container = document.getElementById('tokensList');
        if (!container) {
            console.error('❌ tokensList container not found');
            return;
        }
        
        if (!tokens || tokens.length === 0) {
            displayNoTokens();
            return;
        }
        
        console.log('🎨 Rendering tokens...');
        
        let html = '';
        tokens.forEach((token, index) => {
            // Handle different possible token data formats
            const symbol = token.symbol || token.token_symbol || 'UNKNOWN';
            const price = token.price || token.price_usd || token.current_price || 0;
            const liquidity = token.liquidity || token.liquidity_usd || token.total_liquidity || 0;
            const priceChange = token.price_change_24h || token.price_change_1h || token.change_24h || 0;
            const riskScore = token.risk_score || token.risk || 2.5;
            const age = token.age || token.discovered_at || 'Unknown';
            
            const isPositive = priceChange >= 0;
            const badgeClass = isPositive ? 'bg-success' : 'bg-danger';
            
            html += `
                <div class="token-item border-bottom py-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="d-flex align-items-center">
                                <span class="badge bg-primary me-2">${symbol}</span>
                                <small class="text-muted">$${formatTokenPrice(price)}</small>
                            </div>
                            <div class="small text-muted mt-1">
                                <i class="bi bi-droplet"></i> ${formatLiquidity(liquidity)}
                                <span class="ms-2">
                                    <i class="bi bi-clock"></i> ${age}
                                </span>
                            </div>
                        </div>
                        <div class="text-end">
                            <span class="badge ${badgeClass}">
                                ${isPositive ? '+' : ''}${priceChange.toFixed(2)}%
                            </span>
                            <div class="small text-muted mt-1">
                                Risk: <span class="badge bg-secondary">${riskScore.toFixed(1)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        console.log(`✅ Successfully displayed ${tokens.length} tokens`);
    }
    
    // Helper function for formatting token prices
    function formatTokenPrice(price) {
        const num = parseFloat(price);
        if (isNaN(num) || num === 0) return '0.00';
        
        if (num < 0.000001) return num.toExponential(2);
        if (num < 0.01) return num.toFixed(6);
        return num.toFixed(4);'''
        
        # Find and replace displayTokens function
        display_start = content.find(old_display_start)
        if display_start != -1:
            # Find the end of the function
            brace_count = 0
            pos = display_start
            while pos < len(content):
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = pos + 1
                        break
                pos += 1
            
            if brace_count == 0:
                content = content[:display_start] + new_display_tokens + content[end_pos:]
                print("✅ Replaced displayTokens function")
        
        # Write the updated content back
        dashboard_path.write_text(content, encoding='utf-8')
        
        print("\n✅ Token loading fixes applied successfully!")
        print("\nNext steps:")
        print("1. Restart your server: uvicorn app.main:app --reload")
        print("2. Refresh dashboard: http://127.0.0.1:8000/dashboard")
        print("3. Open browser console (F12) to see detailed token loading logs")
        print("4. You should see: '✅ Successfully displayed X tokens'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

def create_debug_instructions():
    """Create debugging instructions."""
    instructions = """# Debug Token Loading Issues

## Quick Test in Browser Console

1. Open your dashboard: http://127.0.0.1:8000/dashboard
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Run this command:

```javascript
fetch('/api/v1/tokens/discover').then(r => r.json()).then(d => console.log('API Response:', d))
```

## What to Look For

✅ **Success**: You should see an object with `discovered_tokens` array
❌ **Problem**: If you see an error or empty array, the API endpoint needs attention

## Common Issues

1. **API returns empty array**: Token discovery service may not be running
2. **API returns 404**: Endpoint path may be incorrect
3. **API returns 500**: Server error in token discovery logic

## Manual Test Commands

In browser console:
```javascript
// Test the API directly
testTokensAPI()

// Force refresh tokens
refreshTokens()

// Check current tokens data
console.log('Current tokens:', tokensData)
```
"""
    
    with open("debug_tokens.md", "w", encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created debug_tokens.md with troubleshooting guide")

if __name__ == "__main__":
    print("Fix Token Loading Issues")
    print("=" * 30)
    
    if fix_token_loading():
        create_debug_instructions()
        print("\n🎯 If tokens still don't load after restart:")
        print("   Check debug_tokens.md for troubleshooting steps")
    else:
        print("❌ Failed to apply token loading fixes")