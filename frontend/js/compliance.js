// Compliance Checker Module

document.getElementById('checkComplianceBtn').addEventListener('click', checkCompliance);
document.getElementById('rcaFullBtn').addEventListener('click', () => performRCA(false));
document.getElementById('rcaQuickBtn').addEventListener('click', () => performRCA(true));

async function checkCompliance() {
    // Get selected standards
    const standards = [];
    if (document.getElementById('stdFactoryAct').checked) standards.push('Factory_Act');
    if (document.getElementById('stdOISD').checked) standards.push('OISD');
    if (document.getElementById('stdISO').checked) standards.push('ISO_45001');
    
    if (standards.length === 0) {
        showAlert('complianceResult', 'Please select at least one standard.', 'warning');
        return;
    }
    
    showLoading('Checking compliance...');
    
    try {
        const data = await apiRequest('/compliance/check', {
            method: 'POST',
            body: JSON.stringify({ standards })
        });
        
        hideLoading();
        
        if (data.error) {
            showAlert('complianceResult', data.error, 'danger');
            return;
        }
        
        renderComplianceResult(data);
        
    } catch (error) {
        hideLoading();
        showAlert('complianceResult', error.message, 'danger');
    }
}

function renderComplianceResult(data) {
    const resultDiv = document.getElementById('complianceResult');
    const score = data.compliance_score;
    
    // Determine score class
    let scoreClass = 'low';
    let statusBadge = 'bg-danger';
    if (score >= 80) {
        scoreClass = 'high';
        statusBadge = 'bg-success';
    } else if (score >= 60) {
        scoreClass = 'medium';
        statusBadge = 'bg-warning';
    }
    
    let html = `
        <div class="row mb-4">
            <div class="col-md-4 text-center">
                <div class="compliance-score ${scoreClass}">${score}%</div>
                <span class="badge ${statusBadge}">${data.summary.status.replace('_', ' ')}</span>
            </div>
            <div class="col-md-8">
                <div class="row">
                    <div class="col-4 text-center">
                        <h4 class="text-success">${data.summary.compliant}</h4>
                        <small class="text-muted">Compliant</small>
                    </div>
                    <div class="col-4 text-center">
                        <h4 class="text-warning">${data.summary.partial}</h4>
                        <small class="text-muted">Partial</small>
                    </div>
                    <div class="col-4 text-center">
                        <h4 class="text-danger">${data.summary.non_compliant}</h4>
                        <small class="text-muted">Gaps</small>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Findings accordion
    html += `
        <div class="accordion" id="complianceAccordion">
    `;
    
    // Non-compliant items
    if (data.findings.non_compliant.length > 0) {
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button bg-danger text-white" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#nonCompliant">
                        <i class="bi bi-x-circle me-2"></i>
                        Non-Compliant (${data.findings.non_compliant.length})
                    </button>
                </h2>
                <div id="nonCompliant" class="accordion-collapse collapse show">
                    <div class="accordion-body">
                        ${data.findings.non_compliant.map(item => `
                            <div class="compliance-item non-compliant">
                                <strong>${item.standard}</strong>: ${item.requirement}
                                <span class="badge bg-secondary float-end">${item.priority}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Partial compliance
    if (data.findings.partial.length > 0) {
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed bg-warning" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#partialCompliant">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Partial Compliance (${data.findings.partial.length})
                    </button>
                </h2>
                <div id="partialCompliant" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        ${data.findings.partial.map(item => `
                            <div class="compliance-item partial">
                                <strong>${item.standard}</strong>: ${item.requirement}
                                <small class="text-muted ms-2">(${Math.round(item.match_ratio * 100)}% match)</small>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Compliant items
    if (data.findings.compliant.length > 0) {
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed bg-success text-white" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#compliant">
                        <i class="bi bi-check-circle me-2"></i>
                        Compliant (${data.findings.compliant.length})
                    </button>
                </h2>
                <div id="compliant" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        ${data.findings.compliant.map(item => `
                            <div class="compliance-item compliant">
                                <strong>${item.standard}</strong>: ${item.requirement}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    html += `</div>`;
    
    // Action items
    if (data.action_items && data.action_items.length > 0) {
        html += `
            <div class="mt-4">
                <h6><i class="bi bi-list-check me-1"></i>Action Items</h6>
                <table class="table table-sm action-items-table">
                    <thead>
                        <tr>
                            <th>Priority</th>
                            <th>Requirement</th>
                            <th>Action</th>
                            <th>Deadline</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.action_items.slice(0, 5).map(item => `
                            <tr>
                                <td class="priority-${item.priority.toLowerCase()}">${item.priority}</td>
                                <td>${item.requirement}</td>
                                <td>${item.action}</td>
                                <td>${item.deadline}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    resultDiv.innerHTML = html;
}

async function performRCA(quickMode) {
    const equipment = document.getElementById('rcaEquipment').value.trim();
    const failure = document.getElementById('rcaFailure').value.trim();
    const history = document.getElementById('rcaHistory').value.trim();
    
    if (!equipment || !failure) {
        showAlert('rcaResult', 'Please fill in equipment and failure description.', 'warning');
        return;
    }
    
    showLoading(quickMode ? 'Quick analysis...' : 'Performing root cause analysis...');
    
    try {
        const data = await apiRequest('/graph/rca', {
            method: 'POST',
            body: JSON.stringify({
                equipment,
                failure_description: failure,
                historical_context: history,
                quick_mode: quickMode
            })
        });
        
        hideLoading();
        
        if (data.error) {
            renderRCAError(data.error);
            return;
        }
        
        renderRCAResult(data);
        
    } catch (error) {
        hideLoading();
        renderRCAError(error.message);
    }
}

function renderRCAResult(data) {
    const resultDiv = document.getElementById('rcaResult');
    
    resultDiv.innerHTML = `
        <div class="mb-3">
            <span class="badge bg-primary">${data.analysis_type}</span>
            <span class="badge bg-secondary ms-1">${data.equipment}</span>
            <small class="text-muted float-end">${new Date(data.timestamp).toLocaleString()}</small>
        </div>
        <div class="rca-content">
            ${formatResponse(data.analysis)}
        </div>
    `;
}

function renderRCAError(message) {
    const resultDiv = document.getElementById('rcaResult');
    resultDiv.innerHTML = `
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle me-1"></i>
            ${message}
        </div>
    `;
}