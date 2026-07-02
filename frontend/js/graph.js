// Knowledge Graph Module

let network = null;

document.getElementById('buildGraphBtn').addEventListener('click', buildGraph);

async function buildGraph() {
    showLoading('Building knowledge graph...');
    
    try {
        const data = await apiRequest('/graph/build', {
            method: 'POST',
            body: JSON.stringify({})
        });
        
        hideLoading();
        
        if (data.error) {
            showGraphError(data.error);
            return;
        }
        
        if (data.nodes.length === 0) {
            showGraphError('No entities found in documents. Upload documents with equipment references.');
            return;
        }
        
        renderGraph(data.nodes, data.edges);
        updateGraphStats(data.statistics);
        
    } catch (error) {
        hideLoading();
        showGraphError(error.message);
    }
}

function renderGraph(nodes, edges) {
    const container = document.getElementById('graphContainer');
    container.innerHTML = ''; // Clear previous content
    
    // Convert data to vis.js format
    const visNodes = new vis.DataSet(nodes.map(node => ({
        id: node.id,
        label: node.label,
        title: node.title,
        color: {
            background: node.color,
            border: darkenColor(node.color),
            highlight: {
                background: lightenColor(node.color),
                border: node.color
            }
        },
        shape: node.shape || 'box',
        font: { size: 12 },
        size: node.size || 25
    })));
    
    const visEdges = new vis.DataSet(edges.map(edge => ({
        from: edge.from,
        to: edge.to,
        label: edge.label,
        title: edge.title,
        arrows: edge.arrows || 'to',
        color: {
            color: edge.color || '#95a5a6',
            highlight: '#3498db'
        },
        font: { size: 10, align: 'middle' }
    })));
    
    // Network options
    const options = {
        nodes: {
            borderWidth: 2,
            shadow: true
        },
        edges: {
            width: 2,
            shadow: true,
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'horizontal'
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -2000,
                centralGravity: 0.3,
                springLength: 150,
                springConstant: 0.04
            },
            stabilization: {
                iterations: 100
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            hideEdgesOnDrag: true
        },
        layout: {
            improvedLayout: true
        }
    };
    
    // Create network
    network = new vis.Network(container, { nodes: visNodes, edges: visEdges }, options);
    
    // Event handlers
    network.on('click', (params) => {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            showNodeDetails(nodes.find(n => n.id === nodeId));
        }
    });
    
    network.on('stabilizationProgress', (params) => {
        const progress = Math.round((params.iterations / params.total) * 100);
        console.log(`Graph stabilizing: ${progress}%`);
    });
    
    network.on('stabilizationIterationsDone', () => {
        network.setOptions({ physics: { enabled: false } });
    });
}

function showNodeDetails(node) {
    if (!node) return;
    
    const statsDiv = document.getElementById('graphStats');
    statsDiv.innerHTML = `
        <strong>Selected:</strong> ${node.label} 
        <span class="badge bg-secondary ms-1">${node.type}</span>
    `;
}

function updateGraphStats(stats) {
    const statsDiv = document.getElementById('graphStats');
    statsDiv.innerHTML = `
        <span class="me-3"><strong>Nodes:</strong> ${stats.total_nodes}</span>
        <span class="me-3"><strong>Edges:</strong> ${stats.total_edges}</span>
        <span class="me-3"><strong>Equipment:</strong> ${stats.equipment_count}</span>
        <span><strong>Failures:</strong> ${stats.total_failures}</span>
    `;
}

function showGraphError(message) {
    const container = document.getElementById('graphContainer');
    container.innerHTML = `
        <div class="d-flex justify-content-center align-items-center h-100">
            <div class="text-center text-danger">
                <i class="bi bi-exclamation-triangle display-4"></i>
                <p class="mt-2">${message}</p>
            </div>
        </div>
    `;
}

// Color utility functions
function darkenColor(color) {
    return shadeColor(color, -20);
}

function lightenColor(color) {
    return shadeColor(color, 20);
}

function shadeColor(color, percent) {
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    
    return '#' + (
        0x1000000 +
        (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
        (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
        (B < 255 ? (B < 1 ? 0 : B) : 255)
    ).toString(16).slice(1);
}