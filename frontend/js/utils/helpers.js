// Utility helper functions
class Helpers {
    // Format numbers with commas and decimal places
    static formatNumber(number, decimals = 2) {
        if (number === null || number === undefined) return '0';
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }

    // Format percentage
    static formatPercent(value, decimals = 1) {
        if (value === null || value === undefined) return '0%';
        return `${(value * 100).toFixed(decimals)}%`;
    }

    // Format dimensions (length × width × height)
    static formatDimensions(length, width, height, unit = 'cm') {
        return `${this.formatNumber(length)} × ${this.formatNumber(width)} × ${this.formatNumber(height)} ${unit}`;
    }

    // Calculate volume from dimensions
    static calculateVolume(length, width, height) {
        return length * width * height;
    }

    // Convert volume from cm³ to m³
    static cm3ToM3(volume) {
        return volume / 1000000;
    }

    // Convert volume from m³ to cm³
    static m3ToCm3(volume) {
        return volume * 1000000;
    }

    // Generate a unique ID
    static generateId(prefix = '') {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substr(2, 5);
        return `${prefix}${timestamp}${random}`;
    }

    // Debounce function for limiting API calls
    static debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    // Throttle function for limiting frequent calls
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Deep clone an object
    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (obj instanceof Object) {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    }

    // Validate email format
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Validate container dimensions
    static validateContainer(container) {
        const errors = [];
        
        if (!container.name || container.name.trim() === '') {
            errors.push('Container name is required');
        }
        
        if (!container.length || container.length <= 0) {
            errors.push('Container length must be positive');
        }
        
        if (!container.width || container.width <= 0) {
            errors.push('Container width must be positive');
        }
        
        if (!container.height || container.height <= 0) {
            errors.push('Container height must be positive');
        }
        
        if (!container.max_weight || container.max_weight <= 0) {
            errors.push('Container max weight must be positive');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Validate cargo item
    static validateCargoItem(item) {
        const errors = [];
        
        if (!item.id || item.id <= 0) {
            errors.push('Item ID must be positive');
        }
        
        if (!item.name || item.name.trim() === '') {
            errors.push('Item name is required');
        }
        
        if (!item.length || item.length <= 0) {
            errors.push('Item length must be positive');
        }
        
        if (!item.width || item.width <= 0) {
            errors.push('Item width must be positive');
        }
        
        if (!item.height || item.height <= 0) {
            errors.push('Item height must be positive');
        }
        
        if (!item.weight || item.weight <= 0) {
            errors.push('Item weight must be positive');
        }
        
        if (!item.quantity || item.quantity <= 0) {
            errors.push('Item quantity must be positive');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Calculate total items metrics
    static calculateItemsMetrics(items) {
        const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
        const totalVolume = items.reduce((sum, item) => {
            return sum + (item.length * item.width * item.height * item.quantity);
        }, 0);
        const totalWeight = items.reduce((sum, item) => sum + (item.weight * item.quantity), 0);

        return {
            totalItems,
            totalVolume: this.cm3ToM3(totalVolume),
            totalWeight,
            averageVolume: this.cm3ToM3(totalVolume / totalItems),
            averageWeight: totalWeight / totalItems
        };
    }

    // Calculate container utilization
    static calculateUtilization(usedVolume, totalVolume) {
        if (totalVolume <= 0) return 0;
        return Math.min(usedVolume / totalVolume, 1);
    }

    // Generate color based on algorithm type
    static getAlgorithmColor(algorithm) {
        const colors = {
            packing: '#3b82f6',
            genetic: '#10b981',
            stowage: '#f59e0b',
            auto: '#8b5cf6'
        };
        return colors[algorithm] || '#64748b';
    }

    // Format execution time
    static formatExecutionTime(seconds) {
        if (seconds < 1) {
            return `${(seconds * 1000).toFixed(0)}ms`;
        } else if (seconds < 60) {
            return `${seconds.toFixed(2)}s`;
        } else {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
        }
    }

    // Create data URL for download
    static createDownloadUrl(data, filename, type = 'application/json') {
        const blob = new Blob([data], { type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    // Parse CSV data (for future imports)
    static parseCSV(csvText) {
        const lines = csvText.split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        
        return lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            const obj = {};
            headers.forEach((header, index) => {
                obj[header] = values[index] || '';
            });
            return obj;
        }).filter(obj => Object.values(obj).some(val => val !== ''));
    }

    // Export data to CSV
    static exportToCSV(data, filename) {
        if (!data.length) return;

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => 
                headers.map(header => 
                    JSON.stringify(row[header] || '')
                ).join(',')
            )
        ].join('\n');

        this.createDownloadUrl(csvContent, filename, 'text/csv');
    }

    // Local storage helpers
    static saveToLocalStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
            return false;
        }
    }

    static loadFromLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Failed to load from localStorage:', error);
            return defaultValue;
        }
    }

    static removeFromLocalStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
            return false;
        }
    }

    // Date formatting
    static formatDate(date, format = 'medium') {
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            medium: { year: 'numeric', month: 'long', day: 'numeric' },
            long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' },
            time: { hour: '2-digit', minute: '2-digit' }
        };

        return new Intl.DateTimeFormat('en-US', options[format] || options.medium).format(new Date(date));
    }

    // Generate random color (for visualizations)
    static generateColor(seed) {
        const hash = this.hashString(seed);
        const hue = hash % 360;
        return `hsl(${hue}, 70%, 60%)`;
    }

    static hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        return hash;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Helpers;
} else {
    window.Helpers = Helpers;
}