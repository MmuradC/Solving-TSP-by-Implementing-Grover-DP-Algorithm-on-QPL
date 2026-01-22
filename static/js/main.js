let currentResults = {};
let datasetLoaded = false;

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading('Uploading and processing dataset...');
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            datasetLoaded = true;
            displayDatasetInfo(data);
            document.getElementById('visualizationArea').innerHTML = data.visualization;
            hideLoading();
            showSuccess('Dataset loaded successfully!');
        } else {
            hideLoading();
            showError(data.error || 'Upload failed');
        }
    } catch (error) {
        hideLoading();
        showError('Error uploading file: ' + error.message);
    }
}

async function randomizeValues() {
    const numCities = document.getElementById('numCities').value;
    
    try {
        showLoading('Generating random distance matrix...');
        
        const response = await fetch('/randomize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ num_cities: parseInt(numCities) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            datasetLoaded = true;
            document.getElementById('visualizationArea').innerHTML = data.visualization;
            hideLoading();
            showSuccess(`Generated ${data.num_cities} cities`);
        } else {
            hideLoading();
            showError(data.error || 'Randomization failed');
        }
    } catch (error) {
        hideLoading();
        showError('Error: ' + error.message);
    }
}

async function showCircuit() {
    if (!datasetLoaded) {
        showError('Please load a dataset first');
        return;
    }
    
    try {
        showLoading('Building quantum circuit...');
        
        const response = await fetch('/show_circuit', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            const circuitHTML = `
                <div class="result-item">
                    <h4>⚛️ Quantum Circuit</h4>
                    <p><strong>Number of Qubits:</strong> ${data.num_qubits}</p>
                    <p><strong>Circuit Depth:</strong> ${data.circuit_depth}</p>
                    <img src="${data.circuit_image}" style="max-width: 100%; margin-top: 15px;" alt="Quantum Circuit" />
                </div>
            `;
            document.getElementById('resultsArea').innerHTML = circuitHTML;
            hideLoading();
        } else {
            hideLoading();
            showError(data.error || 'Failed to generate circuit');
        }
    } catch (error) {
        hideLoading();
        showError('Error: ' + error.message);
    }
}

async function solveQuantum() {
    if (!datasetLoaded) {
        showError('Please load a dataset first');
        return;
    }
    
    try {
        showLoading('Running quantum algorithm... This may take a moment.');
        
        const response = await fetch('/solve_quantum', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResults['Quantum Grover DP'] = data;
            displayResult('Quantum Grover DP', data);
            hideLoading();
            showSuccess('Quantum solution complete!');
        } else {
            hideLoading();
            showError(data.error || 'Quantum solving failed');
        }
    } catch (error) {
        hideLoading();
        showError('Error: ' + error.message);
    }
}

function showClassicalOptions() {
    if (!datasetLoaded) {
        showError('Please load a dataset first');
        return;
    }
    document.getElementById('classicalOptions').style.display = 'flex';
}

function closeClassicalOptions() {
    document.getElementById('classicalOptions').style.display = 'none';
}

async function solveClassical(algorithm) {
    closeClassicalOptions();
    
    const algorithmNames = {
        'held_karp': 'Held-Karp DP',
        'branch_bound': 'Branch & Bound',
        'greedy': 'Greedy'
    };
    
    try {
        showLoading(`Running ${algorithmNames[algorithm]}...`);
        
        const response = await fetch('/solve_classical', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ algorithm: algorithm })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const name = algorithmNames[algorithm];
            currentResults[name] = data;
            displayResult(name, data);
            hideLoading();
            showSuccess(`${name} solution complete!`);
        } else {
            hideLoading();
            showError(data.error || 'Classical solving failed');
        }
    } catch (error) {
        hideLoading();
        showError('Error: ' + error.message);
    }
}

async function visualizeResults() {
    if (Object.keys(currentResults).length === 0) {
        showError('No results to visualize. Run some algorithms first.');
        return;
    }
    
    try {
        showLoading('Creating visualization...');
        
        const response = await fetch('/visualize_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ results: currentResults })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('visualizationArea').innerHTML = data.visualization;
            hideLoading();
            showSuccess('Visualization updated!');
        } else {
            hideLoading();
            showError(data.error || 'Visualization failed');
        }
    } catch (error) {
        hideLoading();
        showError('Error: ' + error.message);
    }
}

async function saveResults() {
    if (Object.keys(currentResults).length === 0) {
        showError('No results to save. Run some algorithms first.');
        return;
    }
    
    try {
        const response = await fetch('/save_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ results: currentResults })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'tsp_results.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showSuccess('Results saved!');
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to save results');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    }
}

function displayDatasetInfo(data) {
    const infoDiv = document.getElementById('datasetInfo');
    const statsContent = document.getElementById('statsContent');
    
    statsContent.innerHTML = `
        <p><strong>Number of Cities:</strong> ${data.num_cities}</p>
        <p><strong>Rows:</strong> ${data.stats.rows}</p>
        <p><strong>Columns:</strong> ${data.stats.columns}</p>
        <p><strong>Features:</strong> ${escapeHtml(data.stats.features.join(', '))}</p>
    `;
    
    infoDiv.style.display = 'block';
}

function displayResult(name, data) {
    try {
        const tourString = Array.isArray(data.optimal_tour) ? 
            data.optimal_tour.map(x => String(x)).join(' → ') : 
            String(data.optimal_tour);
        
        const cost = parseFloat(data.optimal_cost) || 0;
        const time = parseFloat(data.execution_time) || 0;
        
        const resultHTML = `
            <div class="result-item">
                <h4>${escapeHtml(name)}</h4>
                <p><strong>Optimal Tour:</strong> ${escapeHtml(tourString)}</p>
                <p><strong>Total Cost:</strong> ${cost.toFixed(2)}</p>
                <p><strong>Execution Time:</strong> ${time.toFixed(4)}s</p>
                ${data.quantum_info ? `
                    <p><strong>Iterations:</strong> ${parseInt(data.quantum_info.num_iterations) || 0}</p>
                    <p><strong>Success Probability:</strong> ${((parseFloat(data.quantum_info.success_probability) || 0) * 100).toFixed(2)}%</p>
                ` : ''}
            </div>
        `;
        
        document.getElementById('resultsArea').innerHTML += resultHTML;
    } catch (error) {
        console.error('Error displaying result:', error);
        showError('Error displaying result: ' + error.message);
    }
}

function showLoading(message) {
    const loadingHTML = `
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-content">
                <div class="loading"></div>
                <p>${escapeHtml(message)}</p>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', loadingHTML);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 5px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        background: ${type === 'success' ? '#48bb78' : '#f56565'};
        max-width: 400px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);