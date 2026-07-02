// Document Upload Module

document.getElementById('uploadBtn').addEventListener('click', uploadDocument);

async function uploadDocument() {
    const fileInput = document.getElementById('docFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('uploadStatus', 'Please select a file to upload.', 'warning');
        return;
    }
    
    // Validate file size
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showAlert('uploadStatus', 'File size exceeds 50MB limit.', 'danger');
        return;
    }
    
    // Show progress
    document.getElementById('uploadProgress').classList.remove('d-none');
    document.getElementById('uploadBtn').disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update global state
            appState.documentsUploaded++;
            appState.totalChunks += data.chunks;
            appState.lastMetadata = data.metadata;
            
            // Show success
            document.getElementById('uploadStatus').innerHTML = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle me-1"></i>
                    <strong>${data.filename}</strong> uploaded successfully!
                    <br><small>${data.chunks} chunks processed, ${data.entity_count} entities found</small>
                </div>
            `;
            
            // Update panels
            updateStatsPanel({
                documentsUploaded: appState.documentsUploaded,
                totalChunks: appState.totalChunks,
                vectorCount: data.ingestion_result?.chunks_added
            });
            
            updateMetadataPanel(data.metadata);
            
            // Clear file input
            fileInput.value = '';
            
        } else {
            showAlert('uploadStatus', data.error || 'Upload failed', 'danger');
        }
        
    } catch (error) {
        showAlert('uploadStatus', `Error: ${error.message}`, 'danger');
    } finally {
        document.getElementById('uploadProgress').classList.add('d-none');
        document.getElementById('uploadBtn').disabled = false;
    }
}

// Drag and drop support
const dropZone = document.querySelector('.card-body');

if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-primary');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-primary');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-primary');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            document.getElementById('docFile').files = files;
            uploadDocument();
        }
    });
}