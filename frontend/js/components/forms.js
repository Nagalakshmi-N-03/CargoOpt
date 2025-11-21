/**
 * CargoOpt Form Components
 * Container and item form management
 */

export class ContainerForm {
  constructor(options = {}) {
    this.containerId = options.containerId || 'container-form';
    this.onSubmit = options.onSubmit || (() => {});
    this.onCancel = options.onCancel || (() => {});
    
    this.container = document.getElementById(this.containerId);
    this.items = [];
    this.currentStep = 1;
    
    this.init();
  }
  
  init() {
    this.render();
    this.attachEventListeners();
  }
  
  render() {
    this.container.innerHTML = `
      <div class="form-container">
        <div class="form-header">
          <h2>New Optimization</h2>
          <div class="form-steps">
            <div class="step ${this.currentStep === 1 ? 'active' : ''}" data-step="1">
              <span class="step-number">1</span>
              <span class="step-label">Container</span>
            </div>
            <div class="step ${this.currentStep === 2 ? 'active' : ''}" data-step="2">
              <span class="step-number">2</span>
              <span class="step-label">Items</span>
            </div>
            <div class="step ${this.currentStep === 3 ? 'active' : ''}" data-step="3">
              <span class="step-number">3</span>
              <span class="step-label">Options</span>
            </div>
          </div>
        </div>
        
        <div class="form-body">
          ${this.renderCurrentStep()}
        </div>
        
        <div class="form-footer">
          <button type="button" class="btn btn-secondary" id="cancel-btn">
            <i class="fas fa-times"></i> Cancel
          </button>
          
          ${this.currentStep > 1 ? `
            <button type="button" class="btn btn-secondary" id="prev-btn">
              <i class="fas fa-arrow-left"></i> Previous
            </button>
          ` : ''}
          
          ${this.currentStep < 3 ? `
            <button type="button" class="btn btn-primary" id="next-btn">
              Next <i class="fas fa-arrow-right"></i>
            </button>
          ` : `
            <button type="button" class="btn btn-primary" id="submit-btn">
              <i class="fas fa-play"></i> Start Optimization
            </button>
          `}
        </div>
      </div>
    `;
  }
  
  renderCurrentStep() {
    switch (this.currentStep) {
      case 1:
        return this.renderContainerStep();
      case 2:
        return this.renderItemsStep();
      case 3:
        return this.renderOptionsStep();
      default:
        return '';
    }
  }
  
  renderContainerStep() {
    return `
      <div class="form-step" id="container-step">
        <h3>Container Specifications</h3>
        
        <div class="form-section">
          <label class="form-label">Container Type</label>
          <select id="container-type" class="form-input">
            <option value="custom">Custom Dimensions</option>
            <option value="20ft">20ft Standard (5898 x 2352 x 2393 mm)</option>
            <option value="40ft">40ft Standard (12032 x 2352 x 2393 mm)</option>
            <option value="40ft-hc">40ft High Cube (12032 x 2352 x 2698 mm)</option>
          </select>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="container-length" class="form-label">Length (mm)</label>
            <input type="number" id="container-length" class="form-input" 
                   placeholder="5898" min="100" required>
          </div>
          
          <div class="form-group">
            <label for="container-width" class="form-label">Width (mm)</label>
            <input type="number" id="container-width" class="form-input" 
                   placeholder="2352" min="100" required>
          </div>
          
          <div class="form-group">
            <label for="container-height" class="form-label">Height (mm)</label>
            <input type="number" id="container-height" class="form-input" 
                   placeholder="2393" min="100" required>
          </div>
        </div>
        
        <div class="form-group">
          <label for="container-max-weight" class="form-label">Maximum Weight (kg)</label>
          <input type="number" id="container-max-weight" class="form-input" 
                 placeholder="28000" min="1" step="0.1" required>
        </div>
        
        <div class="form-group">
          <label for="container-name" class="form-label">Container Name (Optional)</label>
          <input type="text" id="container-name" class="form-input" 
                 placeholder="e.g., Container A1">
        </div>
      </div>
    `;
  }
  
  renderItemsStep() {
    return `
      <div class="form-step" id="items-step">
        <div class="items-header">
          <h3>Items to Pack</h3>
          <button type="button" class="btn btn-primary" id="add-item-btn">
            <i class="fas fa-plus"></i> Add Item
          </button>
        </div>
        
        <div class="items-actions">
          <button type="button" class="btn btn-secondary" id="import-items-btn">
            <i class="fas fa-file-import"></i> Import CSV
          </button>
          <button type="button" class="btn btn-secondary" id="quick-add-btn">
            <i class="fas fa-magic"></i> Quick Add
          </button>
        </div>
        
        <div id="items-list" class="items-list">
          ${this.items.length === 0 ? `
            <div class="empty-state">
              <i class="fas fa-box-open fa-3x"></i>
              <p>No items added yet</p>
              <p class="text-muted">Click "Add Item" to start</p>
            </div>
          ` : this.renderItemsList()}
        </div>
        
        <input type="file" id="csv-file-input" accept=".csv" style="display: none;">
      </div>
    `;
  }
  
  renderItemsList() {
    return `
      <div class="items-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Dimensions (L×W×H mm)</th>
              <th>Weight (kg)</th>
              <th>Qty</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${this.items.map((item, index) => `
              <tr data-index="${index}">
                <td>${item.name || 'Item ' + (index + 1)}</td>
                <td>${item.length} × ${item.width} × ${item.height}</td>
                <td>${item.weight}</td>
                <td>${item.quantity || 1}</td>
                <td>
                  <button class="btn-icon" data-action="edit" data-index="${index}">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn-icon" data-action="delete" data-index="${index}">
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      
      <div class="items-summary">
        <p>Total Items: <strong>${this.getTotalItemCount()}</strong></p>
        <p>Total Weight: <strong>${this.getTotalWeight().toFixed(2)} kg</strong></p>
        <p>Total Volume: <strong>${this.getTotalVolume().toFixed(3)} m³</strong></p>
      </div>
    `;
  }
  
  renderOptionsStep() {
    return `
      <div class="form-step" id="options-step">
        <h3>Optimization Options</h3>
        
        <div class="form-group">
          <label for="algorithm" class="form-label">Algorithm</label>
          <select id="algorithm" class="form-input">
            <option value="genetic">Genetic Algorithm (Recommended)</option>
            <option value="constraint">Constraint Programming</option>
            <option value="hybrid">Hybrid Approach</option>
            <option value="auto">Auto-Select</option>
          </select>
          <small class="form-help">Choose the optimization algorithm</small>
        </div>
        
        <div class="form-group">
          <label for="optimize-for" class="form-label">Optimize For</label>
          <select id="optimize-for" class="form-input">
            <option value="balanced">Balanced (Recommended)</option>
            <option value="utilization">Maximum Space Utilization</option>
            <option value="stability">Maximum Stability</option>
            <option value="accessibility">Maximum Accessibility</option>
          </select>
        </div>
        
        <div class="form-section">
          <h4>Advanced Parameters (Optional)</h4>
          
          <div class="form-row">
            <div class="form-group">
              <label for="population-size" class="form-label">Population Size</label>
              <input type="number" id="population-size" class="form-input" 
                     placeholder="100" min="10" max="500">
            </div>
            
            <div class="form-group">
              <label for="generations" class="form-label">Generations</label>
              <input type="number" id="generations" class="form-input" 
                     placeholder="50" min="5" max="500">
            </div>
          </div>
          
          <div class="form-group">
            <label for="time-limit" class="form-label">Time Limit (seconds)</label>
            <input type="number" id="time-limit" class="form-input" 
                   placeholder="300" min="10" max="600">
          </div>
        </div>
        
        <div class="form-section">
          <h4>Preview</h4>
          <div class="optimization-preview">
            <div class="preview-item">
              <i class="fas fa-box"></i>
              <div>
                <strong>Container</strong>
                <p id="preview-container">Not configured</p>
              </div>
            </div>
            <div class="preview-item">
              <i class="fas fa-cubes"></i>
              <div>
                <strong>Items</strong>
                <p id="preview-items">${this.items.length} items</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  
  attachEventListeners() {
    // Navigation buttons
    const cancelBtn = this.container.querySelector('#cancel-btn');
    const prevBtn = this.container.querySelector('#prev-btn');
    const nextBtn = this.container.querySelector('#next-btn');
    const submitBtn = this.container.querySelector('#submit-btn');
    
    cancelBtn?.addEventListener('click', () => this.onCancel());
    prevBtn?.addEventListener('click', () => this.previousStep());
    nextBtn?.addEventListener('click', () => this.nextStep());
    submitBtn?.addEventListener('click', () => this.submit());
    
    // Container type selector
    const containerType = this.container.querySelector('#container-type');
    containerType?.addEventListener('change', (e) => this.onContainerTypeChange(e.target.value));
    
    // Items actions
    const addItemBtn = this.container.querySelector('#add-item-btn');
    const importBtn = this.container.querySelector('#import-items-btn');
    const quickAddBtn = this.container.querySelector('#quick-add-btn');
    
    addItemBtn?.addEventListener('click', () => this.showAddItemModal());
    importBtn?.addEventListener('click', () => this.importItems());
    quickAddBtn?.addEventListener('click', () => this.showQuickAddModal());
    
    // Item actions
    this.container.addEventListener('click', (e) => {
      const action = e.target.closest('[data-action]')?.dataset.action;
      const index = parseInt(e.target.closest('[data-index]')?.dataset.index);
      
      if (action === 'edit' && !isNaN(index)) {
        this.editItem(index);
      } else if (action === 'delete' && !isNaN(index)) {
        this.deleteItem(index);
      }
    });
  }
  
  onContainerTypeChange(type) {
    const presets = {
      '20ft': { length: 5898, width: 2352, height: 2393, maxWeight: 28180 },
      '40ft': { length: 12032, width: 2352, height: 2393, maxWeight: 26680 },
      '40ft-hc': { length: 12032, width: 2352, height: 2698, maxWeight: 26560 },
    };
    
    if (presets[type]) {
      document.getElementById('container-length').value = presets[type].length;
      document.getElementById('container-width').value = presets[type].width;
      document.getElementById('container-height').value = presets[type].height;
      document.getElementById('container-max-weight').value = presets[type].maxWeight;
    }
  }
  
  nextStep() {
    if (this.validateCurrentStep()) {
      this.currentStep++;
      this.render();
      this.attachEventListeners();
    }
  }
  
  previousStep() {
    this.currentStep--;
    this.render();
    this.attachEventListeners();
  }
  
  validateCurrentStep() {
    switch (this.currentStep) {
      case 1:
        return this.validateContainerData();
      case 2:
        return this.validateItemsData();
      case 3:
        return true;
      default:
        return false;
    }
  }
  
  validateContainerData() {
    const length = document.getElementById('container-length')?.value;
    const width = document.getElementById('container-width')?.value;
    const height = document.getElementById('container-height')?.value;
    const maxWeight = document.getElementById('container-max-weight')?.value;
    
    if (!length || !width || !height || !maxWeight) {
      alert('Please fill in all container dimensions');
      return false;
    }
    
    if (length < 100 || width < 100 || height < 100) {
      alert('Container dimensions must be at least 100mm');
      return false;
    }
    
    return true;
  }
  
  validateItemsData() {
    if (this.items.length === 0) {
      alert('Please add at least one item');
      return false;
    }
    return true;
  }
  
  showAddItemModal() {
    // Implementation for add item modal
    const modal = this.createItemModal();
    document.body.appendChild(modal);
  }
  
  createItemModal(item = null, index = null) {
    const isEdit = item !== null;
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>${isEdit ? 'Edit Item' : 'Add Item'}</h3>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Item Name</label>
            <input type="text" id="item-name" class="form-input" 
                   value="${item?.name || ''}" placeholder="e.g., Box A">
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Length (mm)</label>
              <input type="number" id="item-length" class="form-input" 
                     value="${item?.length || ''}" required>
            </div>
            <div class="form-group">
              <label>Width (mm)</label>
              <input type="number" id="item-width" class="form-input" 
                     value="${item?.width || ''}" required>
            </div>
            <div class="form-group">
              <label>Height (mm)</label>
              <input type="number" id="item-height" class="form-input" 
                     value="${item?.height || ''}" required>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Weight (kg)</label>
              <input type="number" id="item-weight" class="form-input" 
                     value="${item?.weight || ''}" step="0.1" required>
            </div>
            <div class="form-group">
              <label>Quantity</label>
              <input type="number" id="item-quantity" class="form-input" 
                     value="${item?.quantity || 1}" min="1" required>
            </div>
          </div>
          <div class="form-group">
            <label><input type="checkbox" id="item-fragile" 
                   ${item?.fragile ? 'checked' : ''}> Fragile</label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary modal-cancel">Cancel</button>
          <button class="btn btn-primary modal-save">
            ${isEdit ? 'Update' : 'Add'}
          </button>
        </div>
      </div>
    `;
    
    modal.querySelector('.modal-close').onclick = () => modal.remove();
    modal.querySelector('.modal-cancel').onclick = () => modal.remove();
    modal.querySelector('.modal-save').onclick = () => {
      const itemData = {
        name: modal.querySelector('#item-name').value,
        length: parseInt(modal.querySelector('#item-length').value),
        width: parseInt(modal.querySelector('#item-width').value),
        height: parseInt(modal.querySelector('#item-height').value),
        weight: parseFloat(modal.querySelector('#item-weight').value),
        quantity: parseInt(modal.querySelector('#item-quantity').value),
        fragile: modal.querySelector('#item-fragile').checked,
      };
      
      if (isEdit) {
        this.items[index] = itemData;
      } else {
        this.items.push(itemData);
      }
      
      this.render();
      this.attachEventListeners();
      modal.remove();
    };
    
    return modal;
  }
  
  editItem(index) {
    const modal = this.createItemModal(this.items[index], index);
    document.body.appendChild(modal);
  }
  
  deleteItem(index) {
    if (confirm('Delete this item?')) {
      this.items.splice(index, 1);
      this.render();
      this.attachEventListeners();
    }
  }
  
  importItems() {
    const input = document.getElementById('csv-file-input');
    input.click();
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        this.parseCSV(file);
      }
    };
  }
  
  async parseCSV(file) {
    // Simple CSV parsing implementation
    const text = await file.text();
    const lines = text.split('\n');
    const headers = lines[0].split(',');
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      if (values.length >= 5) {
        this.items.push({
          name: values[0],
          length: parseInt(values[1]),
          width: parseInt(values[2]),
          height: parseInt(values[3]),
          weight: parseFloat(values[4]),
          quantity: parseInt(values[5]) || 1,
        });
      }
    }
    
    this.render();
    this.attachEventListeners();
  }
  
  showQuickAddModal() {
    // Quick add multiple similar items
    alert('Quick add feature coming soon!');
  }
  
  getTotalItemCount() {
    return this.items.reduce((sum, item) => sum + (item.quantity || 1), 0);
  }
  
  getTotalWeight() {
    return this.items.reduce((sum, item) => 
      sum + (item.weight * (item.quantity || 1)), 0
    );
  }
  
  getTotalVolume() {
    return this.items.reduce((sum, item) => 
      sum + ((item.length * item.width * item.height) * (item.quantity || 1) / 1e9), 0
    );
  }
  
  getData() {
    return {
      container: {
        length: parseInt(document.getElementById('container-length').value),
        width: parseInt(document.getElementById('container-width').value),
        height: parseInt(document.getElementById('container-height').value),
        max_weight: parseFloat(document.getElementById('container-max-weight').value),
        name: document.getElementById('container-name')?.value,
      },
      items: this.items,
      algorithm: document.getElementById('algorithm')?.value || 'genetic',
      parameters: {
        optimize_for: document.getElementById('optimize-for')?.value,
        population_size: document.getElementById('population-size')?.value,
        generations: document.getElementById('generations')?.value,
        time_limit: document.getElementById('time-limit')?.value,
      },
    };
  }
  
  submit() {
    const data = this.getData();
    this.onSubmit(data);
  }
  
  reset() {
    this.items = [];
    this.currentStep = 1;
    this.render();
    this.attachEventListeners();
  }
  
  destroy() {
    this.container.innerHTML = '';
  }
}