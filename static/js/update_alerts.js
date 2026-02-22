/**
 * This script helps update all alert() calls in JavaScript files to use our custom notification system.
 * It's meant to be run in the browser console on each page to identify and update alert calls.
 * 
 * Instructions:
 * 1. Open the page in the browser
 * 2. Open the browser console (F12 or right-click > Inspect > Console)
 * 3. Copy and paste this entire script into the console
 * 4. Run the script
 * 5. Check the console for a list of files that need to be updated
 */

(function() {
    // Find all script elements on the page
    const scripts = document.querySelectorAll('script');
    const alertCalls = [];
    
    // Function to extract alert calls from script content
    function extractAlertCalls(content, scriptSrc) {
        const regex = /alert\s*\(\s*(['"`])(.*?)\1\s*\)/g;
        let match;
        while ((match = regex.exec(content)) !== null) {
            alertCalls.push({
                src: scriptSrc || 'inline script',
                message: match[2],
                fullMatch: match[0],
                index: match.index
            });
        }
    }
    
    // Process inline scripts
    scripts.forEach(script => {
        if (!script.src && script.textContent.includes('alert(')) {
            extractAlertCalls(script.textContent, 'inline script');
        }
    });
    
    // Log the results
    console.log('Found ' + alertCalls.length + ' alert calls:');
    alertCalls.forEach((call, index) => {
        console.log(`${index + 1}. ${call.src}: "${call.message}"`);
        console.log(`   Replace: ${call.fullMatch}`);
        
        // Determine the appropriate replacement function based on the message content
        let replacementFunction = 'showInfo';
        if (call.message.toLowerCase().includes('error') || 
            call.message.toLowerCase().includes('fail') || 
            call.message.toLowerCase().includes('invalid')) {
            replacementFunction = 'showError';
        } else if (call.message.toLowerCase().includes('success')) {
            replacementFunction = 'showSuccess';
        } else if (call.message.toLowerCase().includes('warning')) {
            replacementFunction = 'showWarning';
        }
        
        console.log(`   With: ${replacementFunction}('${call.message}')`);
    });
    
    console.log('\nRecommended steps:');
    console.log('1. Update each JavaScript file to use the appropriate notification function');
    console.log('2. Make sure notifications.js is included on all pages');
    console.log('3. Test each page to ensure notifications work correctly');
    
    return alertCalls;
})(); 