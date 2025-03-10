// NOTE: This file is no longer in use. We've simplified to direct linking to Google Drive.
// Keeping for future reference if we want to implement API integration.

// The ID of your publicly shared Google Drive folder
const FOLDER_ID = '13fWhoHlB9kNXXsHcmKVho2ul6oNRAFIV';

/* 
Previous implementation:

document.addEventListener('DOMContentLoaded', function() {
    // Hide the loader once the iframe is loaded
    const iframe = document.getElementById('drive-folder-iframe');
    const loader = document.getElementById('drive-loader');
    
    if (iframe && loader) {
        iframe.onload = function() {
            loader.style.display = 'none';
            iframe.style.display = 'block';
        };
    }
    
    // Set the correct folder URL
    if (iframe) {
        iframe.src = `https://drive.google.com/embeddedfolderview?id=${FOLDER_ID}#list`;
    }
});
*/
