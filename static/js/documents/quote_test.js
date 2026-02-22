/**
 * Test script for real-time quote preview functionality
 * 
 * This script will automatically test various aspects of the quote creation form
 * and verify the real-time preview updates correctly.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Running quote preview tests...');
    
    // Test utility functions
    
    // Wait for a specified time before continuing
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
    // Set a value on an input field
    function setInputValue(selector, value) {
        const input = document.querySelector(selector);
        if (!input) throw new Error(`Element not found: ${selector}`);
        
        // Set the value
        input.value = value;
        
        // Dispatch input event
        input.dispatchEvent(new Event('input', { bubbles: true }));
        
        return input;
    }
    
    // Select an option from a select dropdown
    function selectOption(selector, optionValue) {
        const select = document.querySelector(selector);
        if (!select) throw new Error(`Select element not found: ${selector}`);
        
        // Find and select the option
        const option = Array.from(select.options).find(opt => opt.value == optionValue);
        if (!option) throw new Error(`Option with value ${optionValue} not found in ${selector}`);
        
        select.value = optionValue;
        select.dispatchEvent(new Event('change', { bubbles: true }));
        
        return select;
    }
    
    // Click a button
    function clickButton(selector) {
        const button = document.querySelector(selector);
        if (!button) throw new Error(`Button not found: ${selector}`);
        button.click();
        return button;
    }
    
    // Check if a value in the preview matches the expected value
    function checkPreviewValue(previewSelector, expectedValue) {
        const previewFrame = document.getElementById('quote-preview-frame');
        if (!previewFrame) throw new Error('Preview frame not found');
        
        const previewDoc = previewFrame.contentDocument || previewFrame.contentWindow.document;
        const element = previewDoc.querySelector(previewSelector);
        
        if (!element) throw new Error(`Preview element not found: ${previewSelector}`);
        
        const actualValue = element.textContent.trim();
        const matches = actualValue.includes(expectedValue.toString().trim());
        
        if (!matches) {
            console.error(`Preview value mismatch for ${previewSelector}:`);
            console.error(`  Expected: ${expectedValue}`);
            console.error(`  Actual: ${actualValue}`);
            return false;
        }
        
        console.log(`✓ Preview value for ${previewSelector} correctly set to: ${actualValue}`);
        return true;
    }
    
    // Run the tests
    async function runTests() {
        try {
            console.log('Starting tests...');
            
            // Wait for the preview frame to load
            await sleep(1000);
            
            // Test 1: Set quote title
            console.log('Test 1: Setting quote title');
            const testTitle = 'Test Quote - ' + new Date().toLocaleTimeString();
            setInputValue('#quote_title', testTitle);
            await sleep(500);
            checkPreviewValue('#preview-document-title', testTitle);
            checkPreviewValue('#preview-project-name', testTitle);
            
            // Test 2: Select a client
            console.log('Test 2: Selecting a client');
            // Get the first client option value that isn't empty
            const clientSelect = document.querySelector('#client');
            let firstClientValue = '';
            
            for (let i = 0; i < clientSelect.options.length; i++) {
                if (clientSelect.options[i].value) {
                    firstClientValue = clientSelect.options[i].value;
                    break;
                }
            }
            
            if (firstClientValue) {
                selectOption('#client', firstClientValue);
                await sleep(1000); // Wait for quote number to be fetched
                
                // Check if quote number was generated
                const quoteNumber = document.querySelector('#quote_number').value;
                if (quoteNumber) {
                    console.log(`✓ Quote number generated: ${quoteNumber}`);
                    checkPreviewValue('#preview-document-number', quoteNumber);
                } else {
                    console.error('❌ Quote number was not generated');
                }
                
                // Check client name in preview
                const clientName = clientSelect.options[clientSelect.selectedIndex].text;
                checkPreviewValue('#preview-client-name', clientName);
            } else {
                console.warn('⚠️ No clients available to select for testing');
            }
            
            // Test 3: Set tax rate
            console.log('Test 3: Setting tax rate');
            const testTaxRate = 15;
            setInputValue('#tax_rate', testTaxRate);
            await sleep(500);
            checkPreviewValue('#preview-tax-rate', testTaxRate);
            
            // Test 4: Add quote items
            console.log('Test 4: Adding and calculating quote items');
            
            // First item is already in the form
            const firstItem = document.querySelector('.quote-item');
            
            // Set values for the first item
            const firstItemInputs = firstItem.querySelectorAll('input');
            firstItemInputs[0].value = 'Service 1'; // Description
            firstItemInputs[1].value = 2; // Quantity
            firstItemInputs[2].value = 1000; // Unit price
            firstItemInputs[3].value = 10; // Discount
            
            // Trigger input events for all fields
            firstItemInputs.forEach(input => {
                input.dispatchEvent(new Event('input', { bubbles: true }));
            });
            
            // Add a second item
            clickButton('#add-item');
            await sleep(500);
            
            // Set values for the second item
            const secondItem = document.querySelectorAll('.quote-item')[1];
            const secondItemInputs = secondItem.querySelectorAll('input');
            secondItemInputs[0].value = 'Service 2'; // Description
            secondItemInputs[1].value = 1; // Quantity
            secondItemInputs[2].value = 5000; // Unit price
            secondItemInputs[3].value = 0; // Discount
            
            // Trigger input events for all fields
            secondItemInputs.forEach(input => {
                input.dispatchEvent(new Event('input', { bubbles: true }));
            });
            
            await sleep(500);
            
            // Calculate expected values
            const item1Total = 2 * 1000 * (1 - 10/100); // 1800
            const item2Total = 1 * 5000; // 5000
            const subtotal = item1Total + item2Total; // 6800
            const tax = subtotal * (testTaxRate / 100); // 1020
            const total = subtotal + tax; // 7820
            
            // Check if the calculations are correct
            checkPreviewValue('#preview-subtotal', subtotal.toFixed(2));
            checkPreviewValue('#preview-tax', tax.toFixed(2));
            checkPreviewValue('#preview-total', total.toFixed(2));
            
            // Check hidden fields
            console.log(`Subtotal field value: ${document.getElementById('subtotal').value}`);
            console.log(`Tax amount field value: ${document.getElementById('tax_amount').value}`);
            console.log(`Total amount field value: ${document.getElementById('total_amount').value}`);
            
            console.log('All tests completed!');
            
        } catch (error) {
            console.error('Test failed:', error);
        }
    }
    
    // Add a test button to the page
    const testButton = document.createElement('button');
    testButton.textContent = 'Run Tests';
    testButton.style.position = 'fixed';
    testButton.style.bottom = '20px';
    testButton.style.right = '20px';
    testButton.style.zIndex = '9999';
    testButton.style.padding = '8px 16px';
    testButton.style.backgroundColor = '#4a6fdc';
    testButton.style.color = 'white';
    testButton.style.border = 'none';
    testButton.style.borderRadius = '4px';
    testButton.style.cursor = 'pointer';
    
    testButton.addEventListener('click', runTests);
    document.body.appendChild(testButton);
}); 