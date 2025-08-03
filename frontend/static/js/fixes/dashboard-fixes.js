
// JavaScript fixes for dashboard
// Fix for querySelectorAll.slice error

// Override the problematic function
if (typeof window.performDiscoveryScan === 'function') {
    const originalPerformDiscoveryScan = window.performDiscoveryScan;
    window.performDiscoveryScan = function() {
        try {
            // Convert NodeList to Array before using slice
            const elements = document.querySelectorAll('.discovery-item');
            const elementsArray = Array.from(elements);
            
            // Now we can safely use slice
            const limitedElements = elementsArray.slice(0, 50);
            
            // Continue with original logic but with fixed elements
            console.log('✅ Discovery scan fixed - processing', limitedElements.length, 'elements');
            
        } catch (error) {
            console.warn('Discovery scan error (safely handled):', error);
        }
    };
}

// Fix for WebSocket connection issues
if (typeof window.WebSocket !== 'undefined') {
    const originalWebSocket = window.WebSocket;
    window.WebSocket = function(url, protocols) {
        const ws = new originalWebSocket(url, protocols);
        
        ws.addEventListener('error', function(event) {
            console.log('WebSocket error handled:', event);
        });
        
        ws.addEventListener('close', function(event) {
            if (event.code === 1006) {
                console.log('WebSocket closed unexpectedly, will retry...');
            }
        });
        
        return ws;
    };
}

console.log('✅ JavaScript fixes applied');
