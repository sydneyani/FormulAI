// Same origin as the page. Set a full origin only if the API is hosted elsewhere.
const backendUrl = '';

// Handle Generate button click
document.getElementById('generate-button').addEventListener('click', function() {
    const query = document.getElementById('query-input').value;
    const resultElement = document.getElementById('result');

    // Add loading animation or text while waiting for the response
    resultElement.innerText = 'Generating...';

    // Send a POST request to the backend to generate the formula
    fetch(`${backendUrl}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        // Add a fade-in effect for the result
        resultElement.style.opacity = 0;
        if (data.formula) {
            resultElement.innerText = `Generated Formula: ${data.formula}`;
        } else {
            resultElement.innerText = data.message || 'Error generating formula. Please try again.';
        }
        resultElement.style.transition = 'opacity 1s';
        resultElement.style.opacity = 1;
    })
    .catch(error => {
        console.error('Error:', error);
        resultElement.innerText = 'Error generating formula. Please try again.';
    });
});

// Handle Excel file upload
document.getElementById('upload-button').addEventListener('click', function(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('file-input');
    const resultElement = document.getElementById('upload-result');
    
    // Check if a file has been selected
    if (fileInput.files.length === 0) {
        resultElement.innerText = 'Please select an Excel file to upload.';
        return;
    }
    
    const file = fileInput.files[0];
    
    // Ensure the file is an Excel file
    if (!file.name.endsWith('.xls') && !file.name.endsWith('.xlsx')) {
        resultElement.innerText = 'Only Excel files (.xls, .xlsx) are allowed.';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Send the file to the backend
    fetch(`${backendUrl}/upload`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json().then(data => ({ ok: response.ok, data })))
    .then(({ ok, data }) => {
        const message = (data && data.message) || '';
        if (!ok || message.toLowerCase().includes('error')) {
            resultElement.innerText = message || 'Upload failed.';
        } else {
            resultElement.innerText = `File uploaded successfully: ${file.name}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        resultElement.innerText = 'Error uploading file. Please try again.';
    });
});
