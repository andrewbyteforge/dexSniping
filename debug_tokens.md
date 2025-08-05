# Debug Token Loading Issues

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
