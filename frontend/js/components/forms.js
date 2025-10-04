// Forms Management Component
class FormsManager {
    constructor(app) {
        this.app = app;
        this.editingContainerIndex = null;
        this.editingItemIndex = null;
    }

    showContainerModal(containerData = null) {
        const modal = document.getElementById('container-modal');
        const title = document.getElementById('container-modal-title');
        const form = document.getElementById('container-form');

        if (containerData) {
            // Pre-fill form with container data
            title.textContent = 'Edit Container';
            document.getElementById('container-name').value = containerData.name || '';
            document.getElementById('container-length').value = containerData.length || '';
            document.getElementById('container-width').value = containerData.width || '';
            document.getElementById('container-height').value = containerData.height || '';
            document.getElementById('container-weight').value = containerData.max_weight || '';
            document.getElementById('container-type').value = containerData.type || 'custom';
            this.editingContainerIndex = null; // We're using standard container data
        } else {
            title.textContent = 'Add Container';
            form.reset();
            this.editingContainerIndex = null;
        }

        modal.classList.add('active');
    }

    editContainer(index) {
        const container = this.app.containers[index];
        this.editingContainerIndex = index;
        
        const modal = document.getElementById('container-modal');
        const title = document.getElementById('container-modal-title');
        
        title.textContent = 'Edit Container';
        document.getElementById('container-name').value = container.name || '';
        document.getElementById('container-length').value = container.length || '';
        document.getElementById('container-width').value = container.width || '';
        document.getElementById('container-height').value = container.height || '';
        document.getElementById('container-weight').value = container.max_weight || '';
        document.getElementById('container-type').value = container.type || 'custom';
        
        modal.classList.add('active');
    }

    saveContainer() {
        const form = document.getElementById('container-form');
        const formData = new FormData(form);

        // Basic validation
        const name = document.getElementById('container-name').value.trim();
        const length = parseFloat(document.getElementById('container-length').value);
        const width = parseFloat(document.getElementById('container-width').value);
        const height = parseFloat(document.getElementById('container-height').value);
        const maxWeight = parseFloat(document.getElementById('container-weight').value);

        if (!name || !length || !width || !height || !maxWeight) {
            this.app.showNotification('Please fill in all required fields', 'error');
            return;
        }

        if (length <= 0 || width <= 0 || height <= 0 || maxWeight <= 0) {
            this.app.showNotification('All values must be positive numbers', 'error');
            return;
        }

        const container = {
            name: name,
            length: length,
            width: width,
            height: height,
            max_weight: maxWeight,
            type: document.getElementById('container-type').value
        };

        if (this.editingContainerIndex !== null) {
            // Update existing container
            this.app.containers[this.editingContainerIndex] = container;
            this.app.showNotification('Container updated successfully', 'success');
        } else {
            // Add new container
            this.app.containers.push(container);
            this.app.showNotification('Container added successfully', 'success');
        }

        // Close modal and refresh display
        document.getElementById('container-modal').classList.remove('active');
        this.app.renderContainers();
        this.app.updatePreviewStats();
        
        this.editingContainerIndex = null;
    }

    showItemModal() {
        const modal = document.getElementById('item-modal');
        const title = document.getElementById('item-modal-title');
        const form = document.getElementById('item-form');

        title.textContent = 'Add Item';
        form.reset();
        this.editingItemIndex = null;

        // Auto-generate ID if no items exist
        if (this.app.items.length === 0) {
            document.getElementById('item-id').value = 1;
        } else {
            const maxId = Math.max(...this.app.items.map(item => item.id));
            document.getElementById('item-id').value = maxId + 1;
        }

        modal.classList.add('active');
    }

    editItem(index) {
        const item = this.app.items[index];
        this.editingItemIndex = index;
        
        const modal = document.getElementById('item-modal');
        const title = document.getElementById('item-modal-title');
        
        title.textContent = 'Edit Item';
        document.getElementById('item-id').value = item.id || '';
        document.getElementById('item-name').value = item.name || '';
        document.getElementById('item-length').value = item.length || '';
        document.getElementById('item-width').value = item.width || '';
        document.getElementById('item-height').value = item.height || '';
        document.getElementById('item-weight').value = item.weight || '';
        document.getElementById('item-quantity').value = item.quantity || 1;
        document.getElementById('item-fragile').checked = item.fragile || false;
        document.getElementById('item-stackable').checked = item.stackable !== false;
        document.getElementById('item-rotation').checked = item.rotation_allowed !== false;
        
        modal.classList.add('active');
    }

    saveItem() {
        const form = document.getElementById('item-form');
        
        // Basic validation
        const id = parseInt(document.getElementById('item-id').value);
        const name = document.getElementById('item-name').value.trim();
        const length = parseFloat(document.getElementById('item-length').value);
        const width = parseFloat(document.getElementById('item-width').value);
        const height = parseFloat(document.getElementById('item-height').value);
        const weight = parseFloat(document.getElementById('item-weight').value);
        const quantity = parseInt(document.getElementById('item-quantity').value);

        if (!id || !name || !length || !width || !height || !weight || !quantity) {
            this.app.showNotification('Please fill in all required fields', 'error');
            return;
        }

        if (id <= 0 || length <= 0 || width <= 0 || height <= 0 || weight <= 0 || quantity <= 0) {
            this.app.showNotification('All values must be positive numbers', 'error');
            return;
        }

        // Check for duplicate ID
        if (this.editingItemIndex === null) {
            const existingItem = this.app.items.find(item => item.id === id);
            if (existingItem) {
                this.app.showNotification('Item ID already exists', 'error');
                return;
            }
        }

        const item = {
            id: id,
            name: name,
            length: length,
            width: width,
            height: height,
            weight: weight,
            quantity: quantity,
            fragile: document.getElementById('item-fragile').checked,
            stackable: document.getElementById('item-stackable').checked,
            rotation_allowed: document.getElementById('item-rotation').checked
        };

        if (this.editingItemIndex !== null) {
            // Update existing item
            this.app.items[this.editingItemIndex] = item;
            this.app.showNotification('Item updated successfully', 'success');
        } else {
            // Add new item
            this.app.items.push(item);
            this.app.showNotification('Item added successfully', 'success');
        }

        // Close modal and refresh display
        document.getElementById('item-modal').classList.remove('active');
        this.app.renderItems();
        this.app.updatePreviewStats();
        
        this.editingItemIndex = null;
    }

    // Utility method to generate sample data for testing
    generateSampleData() {
        // Sample containers
        this.app.containers = [
            {
                name: "Standard 20ft Container",
                length: 605,
                width: 244,
                height: 259,
                max_weight: 28200,
                type: "standard_20ft"
            },
            {
                name: "High Cube 40ft Container",
                length: 1219,
                width: 244,
                height: 289,
                max_weight: 26700,
                type: "high_cube_40ft"
            }
        ];

        // Sample items
        this.app.items = [
            {
                id: 1,
                name: "Small Box",
                length: 50,
                width: 40,
                height: 30,
                weight: 10,
                quantity: 10,
                fragile: false,
                stackable: true,
                rotation_allowed: true
            },
            {
                id: 2,
                name: "Medium Crate",
                length: 120,
                width: 80,
                height: 60,
                weight: 50,
                quantity: 5,
                fragile: false,
                stackable: true,
                rotation_allowed: true
            },
            {
                id: 3,
                name: "Large Pallet",
                length: 200,
                width: 120,
                height: 100,
                weight: 200,
                quantity: 3,
                fragile: false,
                stackable: true,
                rotation_allowed: false
            },
            {
                id: 4,
                name: "Fragile Equipment",
                length: 80,
                width: 60,
                height: 40,
                weight: 30,
                quantity: 2,
                fragile: true,
                stackable: false,
                rotation_allowed: false
            }
        ];

        this.app.renderContainers();
        this.app.renderItems();
        this.app.updatePreviewStats();
        this.app.showNotification('Sample data loaded successfully', 'success');
    }
}