// Forms Manager - Handles all form-related operations
class FormsManager {
    constructor(app) {
        this.app = app;
        this.editingContainerIndex = null;
        this.editingItemIndex = null;
    }

    // Container Modal
    showContainerModal(data = null) {
        const modal = document.getElementById('container-modal');
        const title = document.getElementById('container-modal-title');
        
        if (data) {
            // Edit mode
            title.textContent = 'Edit Container';
            document.getElementById('container-name').value = data.name || '';
            document.getElementById('container-length').value = data.length || '';
            document.getElementById('container-width').value = data.width || '';
            document.getElementById('container-height').value = data.height || '';
            document.getElementById('container-weight').value = data.max_weight || '';
            document.getElementById('container-type').value = data.type || 'custom';
        } else {
            // Add mode
            title.textContent = 'Add Container';
            document.getElementById('container-form').reset();
        }
        
        modal.classList.add('active');
    }

    saveContainer() {
        const form = document.getElementById('container-form');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const container = {
            id: this.editingContainerIndex !== null ? 
                this.app.containers[this.editingContainerIndex].id : 
                Date.now(),
            name: document.getElementById('container-name').value,
            length: parseFloat(document.getElementById('container-length').value),
            width: parseFloat(document.getElementById('container-width').value),
            height: parseFloat(document.getElementById('container-height').value),
            max_weight: parseFloat(document.getElementById('container-weight').value),
            type: document.getElementById('container-type').value
        };

        if (this.editingContainerIndex !== null) {
            this.app.containers[this.editingContainerIndex] = container;
            this.app.showNotification('Container updated', 'success');
            this.editingContainerIndex = null;
        } else {
            this.app.containers.push(container);
            this.app.showNotification('Container added', 'success');
        }

        this.app.renderContainers();
        this.app.updatePreviewStats();
        
        document.getElementById('container-modal').classList.remove('active');
        form.reset();
    }

    editContainer(index) {
        this.editingContainerIndex = index;
        this.showContainerModal(this.app.containers[index]);
    }

    // Item Modal
    showItemModal(data = null) {
        const modal = document.getElementById('item-modal');
        const title = document.getElementById('item-modal-title');
        
        if (data) {
            // Edit mode
            title.textContent = 'Edit Item';
            document.getElementById('item-id').value = data.id || '';
            document.getElementById('item-name').value = data.name || '';
            document.getElementById('item-length').value = data.length || '';
            document.getElementById('item-width').value = data.width || '';
            document.getElementById('item-height').value = data.height || '';
            document.getElementById('item-weight').value = data.weight || '';
            document.getElementById('item-quantity').value = data.quantity || 1;
            document.getElementById('item-fragile').checked = data.fragile || false;
            document.getElementById('item-stackable').checked = data.stackable !== false;
            document.getElementById('item-rotation').checked = data.rotation_allowed !== false;
        } else {
            // Add mode
            title.textContent = 'Add Item';
            const form = document.getElementById('item-form');
            form.reset();
            // Set default ID
            const nextId = this.app.items.length > 0 ? 
                Math.max(...this.app.items.map(i => i.id)) + 1 : 1;
            document.getElementById('item-id').value = nextId;
        }
        
        modal.classList.add('active');
    }

    saveItem() {
        const form = document.getElementById('item-form');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const item = {
            id: parseInt(document.getElementById('item-id').value),
            name: document.getElementById('item-name').value,
            length: parseFloat(document.getElementById('item-length').value),
            width: parseFloat(document.getElementById('item-width').value),
            height: parseFloat(document.getElementById('item-height').value),
            weight: parseFloat(document.getElementById('item-weight').value),
            quantity: parseInt(document.getElementById('item-quantity').value),
            fragile: document.getElementById('item-fragile').checked,
            stackable: document.getElementById('item-stackable').checked,
            rotation_allowed: document.getElementById('item-rotation').checked
        };

        // Calculate volume
        item.volume = item.length * item.width * item.height;

        if (this.editingItemIndex !== null) {
            this.app.items[this.editingItemIndex] = item;
            this.app.showNotification('Item updated', 'success');
            this.editingItemIndex = null;
        } else {
            // Check if ID already exists
            if (this.app.items.some(i => i.id === item.id)) {
                this.app.showNotification('Item ID already exists', 'error');
                return;
            }
            this.app.items.push(item);
            this.app.showNotification('Item added', 'success');
        }

        this.app.renderItems();
        this.app.updatePreviewStats();
        
        document.getElementById('item-modal').classList.remove('active');
        form.reset();
    }

    editItem(index) {
        this.editingItemIndex = index;
        this.showItemModal(this.app.items[index]);
    }

    // Generate Sample Data
    generateSampleData() {
        if (this.app.containers.length === 0) {
            // Add a sample container
            this.app.containers.push({
                id: 1,
                name: 'Standard 20ft Container',
                length: 589,
                width: 235,
                height: 239,
                max_weight: 28200,
                type: 'standard_20ft'
            });
        }

        // Add sample items
        const sampleItems = [
            { id: 1, name: 'Small Box', length: 50, width: 40, height: 30, weight: 10, quantity: 10 },
            { id: 2, name: 'Medium Crate', length: 120, width: 80, height: 60, weight: 50, quantity: 5 },
            { id: 3, name: 'Large Pallet', length: 200, width: 120, height: 100, weight: 200, quantity: 3 },
            { id: 4, name: 'Fragile Equipment', length: 80, width: 60, height: 40, weight: 30, quantity: 2, fragile: true }
        ];

        sampleItems.forEach(item => {
            if (!this.app.items.some(i => i.id === item.id)) {
                this.app.items.push({
                    ...item,
                    volume: item.length * item.width * item.height,
                    fragile: item.fragile || false,
                    stackable: true,
                    rotation_allowed: true
                });
            }
        });

        this.app.renderContainers();
        this.app.renderItems();
        this.app.updatePreviewStats();
        this.app.showNotification('Sample data loaded', 'success');
    }
}