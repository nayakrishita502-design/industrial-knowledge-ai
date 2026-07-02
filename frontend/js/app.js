// Industrial Knowledge AI - Main Application Script

const API_BASE = '[localhost](http://localhost:5000/api)';

// Global state
const appState = {
    documentsUploaded: 0,
    totalChunks: 0,
    lastMetadata: null,
    graphData: null
};

// Loading modal control
const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));

function showLoading(message = 'Processing...') {
    document.getElementById('loadingText').textContent = message;
    loadingModal.show();
}

function hideLoading() {
    loadingModal.hide();
}

// API helper functions
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Check API health on load
async function checkAPIHealth() {
    try {
        const data = await apiRequest('/health');
        updateConnectionStatus(true, data.google_api_configured);
    } catch (error) {
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected, apiConfigured = false) {
    const statusEl = document.getElementById('connectionStatus');
    
    if (connected) {
        if (apiConfigured) {
            statusEl.innerHTML = '<i class="bi bi-circle-fill text-success me-1"></i> Connected';
        } else {
            statusEl.innerHTML = '<i class="bi bi-circle-fill text-warning me-1"></i> API Key Missing';
        }
    } else {
        statusEl.innerHTML = '<i class="bi bi-circle-fill text-danger me-1"></i> Disconnected';
    }
}

// Update stats panel
function updateStatsPanel(stats) {
    const panel = document.getElementById('statsPanel');
    
    if (!stats || stats.documentsUploaded === 0) {
        panel.innerHTML = '<p class="text-muted small mb-0">No documents uploaded</p>';
        return;
    }
    
    panel.innerHTML = `
        <div class="stat-item">
            <span>Documents</span>
            <span class="stat-value">${stats.documentsUploaded}</span>
        </div>
        <div class="stat-item">
            <span>Total Chunks</span>
            <span class="stat-value">${stats.totalChunks}</span>
        </div>
        <div class="stat-item">
            <span>Vector Store</span>
            <span class="stat-value">${stats.vectorCount || 'N/A'}</span>
        </div>
    `;
}

// Update metadata panel
function updateMetadataPanel(metadata) {
    const panel = document.getElementById('metadataPanel');
    
    if (!metadata) {
        panel.innerHTML = '<p class="text-muted small mb-0">Upload a document to see metadata</p>';
        return;
    }
    
    let html = '';
    
    if (metadata.equipment && metadata.equipment.length > 0) {
        html += '<p class="mb-1"><strong>Equipment:</strong></p>';
        html += metadata.equipment.map(e => 
            `<span class="metadata-tag equipment">${e}</span>`
        ).join('');
    }
    
    if (metadata.hazards && metadata.hazards.length > 0) {
        html += '<p class="mb-1 mt-2"><strong>Hazards:</strong></p>';
        html += metadata.hazards.map(h => 
            `<span class="metadata-tag hazard">${h}</span>`
        ).join('');
    }
    
    if (metadata.procedures && metadata.procedures.length > 0) {
        html += '<p class="mb-1 mt-2"><strong>Procedures:</strong></p>';
        html += metadata.procedures.map(p => 
            `<span class="metadata-tag procedure">${p}</span>`
        ).join('');
    }
    
    if (metadata.dates && metadata.dates.length > 0) {
        html += '<p class="mb-1 mt-2"><strong>Dates:</strong></p>';
        html += metadata.dates.map(d => 
            `<span class="metadata-tag date">${d}</span>`
        ).join('');
    }
    
    if (metadata.personnel && metadata.personnel.length > 0) {
        html += '<p class="mb-1 mt-2"><strong>Personnel:</strong></p>';
        html += metadata.personnel.map(p => 
            `<span class="metadata-tag">${p}</span>`
        ).join('');
    }
    
    panel.innerHTML = html || '<p class="text-muted small mb-0">No metadata extracted</p>';
}

// Show alert message
function showAlert(container, message, type = 'danger') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const alertContainer = document.getElementById(container);
    alertContainer.innerHTML = alertHtml;
}

// Format markdown-like text
function formatResponse(text) {
    // Convert headers
    text = text.replace(/### (.*?)$/gm, '<h6 class="mt-3 mb-2">$1</h6>');
    text = text.replace(/## (.*?)$/gm, '<h5 class="mt-3 mb-2">$1</h5>');
    
    // Convert bold
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet points
    text = text.replace(/^- (.*?)$/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>\n?)+/g, '<ul class="mb-2">$&</ul>');
    
    // Convert line breaks
    text = text.replace(/\n\n/g, '</p><p>');
    text = text.replace(/\n/g, '<br>');
    
    return `<p>${text}</p>`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAPIHealth();
    
    // Refresh stats every 30 seconds
    setInterval(checkAPIHealth, 30000);
});