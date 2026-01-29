// Utility Functions - API calls, toast notifications, loading spinner

const API_BASE_URL = '/api';

// API Helper Functions
const api = {
    async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };
        
        if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
            config.body = JSON.stringify(config.body);
        }

        if (config.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'An error occurred');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, body) {
        return this.request(endpoint, { method: 'POST', body });
    },

    put(endpoint, body) {
        return this.request(endpoint, { method: 'PUT', body });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },
};

// Toast Notification System
const toast = {
    container: null,

    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', title = '', duration = 5000) {
        this.init();

        const toastEl = document.createElement('div');
        toastEl.className = `toast ${type}`;

        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };

        const titles = {
            success: title || 'Success',
            error: title || 'Error',
            warning: title || 'Warning',
            info: title || 'Info'
        };

        toastEl.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-title">${titles[type]}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Close">&times;</button>
        `;

        this.container.appendChild(toastEl);

        const closeBtn = toastEl.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.hide(toastEl));

        setTimeout(() => {
            toastEl.style.opacity = '1';
        }, 10);

        if (duration > 0) {
            setTimeout(() => {
                this.hide(toastEl);
            }, duration);
        }

        return toastEl;
    },

    hide(toastEl) {
        toastEl.classList.add('hiding');
        setTimeout(() => {
            if (toastEl.parentNode) {
                toastEl.parentNode.removeChild(toastEl);
            }
        }, 300);
    },

    success(message, title = '') {
        return this.show(message, 'success', title);
    },

    error(message, title = '') {
        return this.show(message, 'error', title);
    },

    warning(message, title = '') {
        return this.show(message, 'warning', title);
    },

    info(message, title = '') {
        return this.show(message, 'info', title);
    }
};

// Loading Spinner
const loader = {
    overlay: null,

    init() {
        if (!this.overlay) {
            this.overlay = document.createElement('div');
            this.overlay.className = 'loader-overlay';
            this.overlay.innerHTML = `
                <div>
                    <div class="loader"></div>
                    <div class="loader-text" id="loader-text">Loading...</div>
                </div>
            `;
            document.body.appendChild(this.overlay);
        }
    },

    show(text = 'Loading...') {
        this.init();
        const textEl = this.overlay.querySelector('#loader-text');
        if (textEl) {
            textEl.textContent = text;
        }
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    },

    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
};

// Modal Helper
const modal = {
    open(modalId) {
        const overlay = document.getElementById(modalId);
        if (overlay) {
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            const closeBtn = overlay.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.onclick = () => this.close(modalId);
            }
            
            overlay.onclick = (e) => {
                if (e.target === overlay) {
                    this.close(modalId);
                }
            };
        }
    },

    close(modalId) {
        const overlay = document.getElementById(modalId);
        if (overlay) {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
};

// Form Validation
const validation = {
    email(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    password(password) {
        return password.length >= 8;
    },

    required(value) {
        return value !== null && value !== undefined && value.trim() !== '';
    },

    showError(inputEl, message) {
        const formGroup = inputEl.closest('.form-group');
        if (!formGroup) return;

        this.clearError(inputEl);

        const errorEl = document.createElement('div');
        errorEl.className = 'form-error';
        errorEl.textContent = message;
        formGroup.appendChild(errorEl);

        inputEl.classList.add('error');
    },

    clearError(inputEl) {
        const formGroup = inputEl.closest('.form-group');
        if (!formGroup) return;

        const errorEl = formGroup.querySelector('.form-error');
        if (errorEl) {
            errorEl.remove();
        }

        inputEl.classList.remove('error');
    },

    validateForm(formEl) {
        const inputs = formEl.querySelectorAll('[required]');
        let isValid = true;

        inputs.forEach(input => {
            this.clearError(input);

            if (!this.required(input.value)) {
                this.showError(input, 'This field is required');
                isValid = false;
            } else if (input.type === 'email' && !this.email(input.value)) {
                this.showError(input, 'Please enter a valid email address');
                isValid = false;
            } else if (input.type === 'password' && !this.password(input.value)) {
                this.showError(input, 'Password must be at least 8 characters');
                isValid = false;
            }
        });

        return isValid;
    }
};

// Local Storage Helper
const storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Storage error:', error);
        }
    },

    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Storage error:', error);
            return defaultValue;
        }
    },

    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Storage error:', error);
        }
    },

    clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Storage error:', error);
        }
    }
};

// Date/Time Formatting
const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1
    };

    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
        }
    }

    return 'just now';
};

// File Size Formatting
const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

// Debounce Function
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Copy to Clipboard
const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        toast.success('Copied to clipboard');
    } catch (error) {
        toast.error('Failed to copy to clipboard');
    }
};

// Download File
const downloadFile = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        api,
        toast,
        loader,
        modal,
        validation,
        storage,
        formatDate,
        formatDateTime,
        timeAgo,
        formatFileSize,
        debounce,
        copyToClipboard,
        downloadFile
    };
}
