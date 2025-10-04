// Results Management Component
class ResultsManager {
    constructor(app) {
        this.app = app;
    }

    displayResults(result) {
        this.updateMetrics(result);
        this.displayPlacements(result);
        this.createVisualization(result);
    }

    updateMetrics(result) {
        const metrics = result.result?.metrics || {};
        
        // Update main metrics cards
        document.getElementById('metric-utilization').textContent = 
            `${(metrics.utilization_rate * 100).toFixed(1)}%`;
        document.getElementById('metric-items').textContent = 
            metrics.total_items_packed || 0;
        document.getElementById('metric-weight').textContent = 
            metrics.weight_utilization ? `${(metrics.weight_utilization * 100).toFixed(1)}%` : 'N/A';
        document.getElementById('metric-efficiency').textContent = 
            metrics.efficiency_score ? `${(metrics.efficiency_score * 100).toFixed(1)}%` : 'N/A';

        // Update detailed metrics if available
        if (metrics.volume_metrics) {
            document.getElementById('metric-utilization').textContent = 
                `${(metrics.volume_metrics.utilization_rate * 100).toFixed(1)}%`;
        }
    }

    displayPlacements(result) {
        const placements = result.result?.placements || [];
        const tableBody = document.getElementById('placements-table-body');
        
        tableBody.innerHTML = '';

        if (placements.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">
                        <div class="empty-state">
                            <i class="fas fa-box"></i>
                            <p>No placement data available</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        placements.forEach(placement => {
            const row = document.createElement('tr');
            const volume = placement.dimensions[0] * placement.dimensions[1] * placement.dimensions[2];
            
            row.innerHTML = `
                <td>${placement.item_id}</td>
                <td>(${placement.position[0].toFixed(1)}, ${placement.position[1].toFixed(1)}, ${placement.position[2].toFixed(1)})</td>
                <td>${placement.dimensions[0]}×${placement.dimensions[1]}×${placement.dimensions[2]}</td>
                <td>${placement.rotated ? 'Yes' : 'No'}</td>
                <td>${volume.toFixed(1)} cm³</td>
            `;
            tableBody.appendChild(row);
        });
    }

    createVisualization(result) {
        const container = document.getElementById('visualization-container');
        const placements = result.result?.placements || [];
        
        if (placements.length === 0) {
            container.innerHTML = `
                <div class="visualization-placeholder">
                    <i class="fas fa-cube"></i>
                    <p>No placement data available for visualization</p>
                </div>
            `;
            return;
        }

        // Simple 2D visualization using CSS
        // In a real application, you might use Three.js for 3D visualization
        container.innerHTML = `
            <div class="visualization-2d">
                <div class="viz-header">
                    <h4>2D Placement Visualization (Top View)</h4>
                    <div class="viz-legend">
                        <div class="legend-item">
                            <div class="legend-color" style="background: #3b82f6"></div>
                            <span>Items</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #ef4444"></div>
                            <span>Container</span>
                        </div>
                    </div>
                </div>
                <div class="viz-canvas" id="viz-canvas">
                    <!-- Visualization will be generated here -->
                </div>
                <div class="viz-info">
                    <p>Showing ${placements.length} placed items</p>
                    <p>Use mouse to pan and zoom (if supported)</p>
                </div>
            </div>
        `;

        this.generate2DVisualization(placements, result.result?.container_data);
    }

    generate2DVisualization(placements, containerData) {
        const canvas = document.getElementById('viz-canvas');
        
        if (!containerData && this.app.containers.length > 0) {
            containerData = this.app.containers[0];
        }

        if (!containerData) return;

        // Create a simple SVG visualization
        const svgNS = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(svgNS, "svg");
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "400");
        svg.setAttribute("viewBox", `0 0 ${containerData.length} ${containerData.width}`);

        // Draw container outline
        const containerRect = document.createElementNS(svgNS, "rect");
        containerRect.setAttribute("x", "0");
        containerRect.setAttribute("y", "0");
        containerRect.setAttribute("width", containerData.length.toString());
        containerRect.setAttribute("height", containerData.width.toString());
        containerRect.setAttribute("fill", "none");
        containerRect.setAttribute("stroke", "#ef4444");
        containerRect.setAttribute("stroke-width", "2");
        containerRect.setAttribute("stroke-dasharray", "5,5");
        svg.appendChild(containerRect);

        // Draw placements
        placements.forEach((placement, index) => {
            const rect = document.createElementNS(svgNS, "rect");
            rect.setAttribute("x", placement.position[0].toString());
            rect.setAttribute("y", placement.position[1].toString());
            rect.setAttribute("width", placement.dimensions[0].toString());
            rect.setAttribute("height", placement.dimensions[1].toString());
            rect.setAttribute("fill", "#3b82f6");
            rect.setAttribute("fill-opacity", "0.7");
            rect.setAttribute("stroke", "#1d4ed8");
            rect.setAttribute("stroke-width", "1");
            
            // Add tooltip
            rect.setAttribute("data-item-id", placement.item_id);
            rect.addEventListener('mouseenter', (e) => {
                this.showTooltip(e, placement);
            });
            rect.addEventListener('mouseleave', this.hideTooltip);
            
            svg.appendChild(rect);

            // Add item ID label
            const text = document.createElementNS(svgNS, "text");
            text.setAttribute("x", (placement.position[0] + placement.dimensions[0] / 2).toString());
            text.setAttribute("y", (placement.position[1] + placement.dimensions[1] / 2).toString());
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("dominant-baseline", "central");
            text.setAttribute("fill", "white");
            text.setAttribute("font-size", "12");
            text.setAttribute("font-weight", "bold");
            text.textContent = placement.item_id.toString();
            svg.appendChild(text);
        });

        canvas.appendChild(svg);
    }

    showTooltip(event, placement) {
        // Create or update tooltip
        let tooltip = document.getElementById('viz-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'viz-tooltip';
            tooltip.className = 'viz-tooltip';
            document.body.appendChild(tooltip);
        }

        const volume = placement.dimensions[0] * placement.dimensions[1] * placement.dimensions[2];
        
        tooltip.innerHTML = `
            <strong>Item ${placement.item_id}</strong><br>
            Position: (${placement.position[0].toFixed(1)}, ${placement.position[1].toFixed(1)}, ${placement.position[2].toFixed(1)})<br>
            Dimensions: ${placement.dimensions[0]}×${placement.dimensions[1]}×${placement.dimensions[2]}<br>
            Volume: ${volume.toFixed(1)} cm³<br>
            ${placement.rotated ? 'Rotated: Yes' : ''}
        `;

        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY + 10) + 'px';
        tooltip.style.display = 'block';
    }

    hideTooltip() {
        const tooltip = document.getElementById('viz-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }

    displayComparison(comparisonResult) {
        const resultsContainer = document.getElementById('optimization-results');
        
        if (!comparisonResult.comparison) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-balance-scale"></i>
                    <p>No comparison data available</p>
                </div>
            `;
            return;
        }

        const comparison = comparisonResult.comparison.comparison || {};
        const bestAlgorithm = comparisonResult.best_algorithm;
        
        let comparisonHTML = `
            <div class="comparison-results">
                <div class="comparison-header">
                    <h3>Algorithm Comparison</h3>
                    <div class="best-algorithm">
                        <i class="fas fa-trophy"></i>
                        Best Algorithm: <strong>${bestAlgorithm}</strong>
                    </div>
                </div>
                <div class="comparison-grid">
        `;

        Object.entries(comparison).forEach(([algorithm, metrics]) => {
            const isBest = algorithm === bestAlgorithm;
            comparisonHTML += `
                <div class="comparison-card ${isBest ? 'best' : ''}">
                    <div class="algorithm-name">${algorithm.toUpperCase()}</div>
                    <div class="comparison-metrics">
                        <div class="comparison-metric">
                            <span class="metric-label">Utilization:</span>
                            <span class="metric-value">${(metrics.utilization_rate * 100).toFixed(1)}%</span>
                        </div>
                        <div class="comparison-metric">
                            <span class="metric-label">Items Packed:</span>
                            <span class="metric-value">${metrics.total_items_packed}</span>
                        </div>
                        <div class="comparison-metric">
                            <span class="metric-label">Execution Time:</span>
                            <span class="metric-value">${metrics.execution_time.toFixed(2)}s</span>
                        </div>
                        <div class="comparison-metric">
                            <span class="metric-label">Efficiency:</span>
                            <span class="metric-value">${(metrics.efficiency_score * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                    ${isBest ? '<div class="best-badge">Best</div>' : ''}
                </div>
            `;
        });

        comparisonHTML += `
                </div>
                <div class="comparison-recommendations">
                    <h4>Recommendations</h4>
                    <ul>
                        ${comparisonResult.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

        resultsContainer.innerHTML = comparisonHTML;
    }

    displayHistory(history) {
        const tableBody = document.getElementById('history-table-body');
        
        tableBody.innerHTML = '';

        if (!history || history.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">
                        <div class="empty-state">
                            <i class="fas fa-history"></i>
                            <p>No optimization history found</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        history.forEach(record => {
            const row = document.createElement('tr');
            const date = new Date(record.created_at).toLocaleDateString();
            
            row.innerHTML = `
                <td>${date}</td>
                <td>
                    <span class="algorithm-tag algorithm-${record.algorithm}">
                        ${record.algorithm}
                    </span>
                </td>
                <td>${(record.utilization_rate * 100).toFixed(1)}%</td>
                <td>${record.total_items_packed}</td>
                <td>${record.execution_time.toFixed(2)}s</td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="app.viewHistoryResult('${record.id}')">
                        <i class="fas fa-eye"></i>
                        View
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }

    // Method to view a specific historical result
    async viewHistoryResult(resultId) {
        // This would typically fetch the full result from the backend
        // For now, we'll just show a notification
        this.app.showNotification(`Viewing historical result ${resultId} would fetch detailed data from the backend`, 'info');
    }

    // Export results functionality
    exportResults(result, format = 'excel') {
        this.app.showNotification(`Exporting results in ${format} format...`, 'info');
        
        // In a real implementation, this would call the backend export endpoint
        // For now, we'll create a simple JSON download
        const dataStr = JSON.stringify(result, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `cargo-optimization-result-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        this.app.showNotification('Results exported successfully', 'success');
    }
}