/**
 * Modern Dashboard JavaScript for Kynetik Electric Field Service
 */

class KynetikDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupRealTimeUpdates();
    }

    setupEventListeners() {
        document.addEventListener('click', this.handleClick.bind(this));
        document.addEventListener('change', this.handleChange.bind(this));
        
        // File upload handling
        this.setupFileUpload();
        
        // Form submissions
        this.setupFormHandlers();
        
        // Mobile optimizations
        this.setupMobileHandlers();
    }

    handleClick(e) {
        const target = e.target;
        
        // Job status updates
        if (target.matches('.start-job-btn')) {
            this.updateJobStatus(target.dataset.jobId, 'in_progress');
        } else if (target.matches('.complete-job-btn')) {
            this.updateJobStatus(target.dataset.jobId, 'completed');
        } else if (target.matches('.pause-job-btn')) {
            this.updateJobStatus(target.dataset.jobId, 'on_hold');
        }
        
        // File upload triggers
        else if (target.matches('.upload-btn')) {
            this.triggerFileUpload(target.dataset.jobId);
        }
        
        // Camera capture for mobile
        else if (target.matches('.camera-btn')) {
            this.triggerCameraCapture(target.dataset.jobId);
        }
        
        // Toolie chat
        else if (target.matches('.toolie-bubble') || target.closest('.toolie-bubble')) {
            this.toggleToolieChat();
        }
    }

    handleChange(e) {
        const target = e.target;
        
        // Status filters
        if (target.name === 'statusFilter' || target.name === 'adminFilter') {
            this.filterJobs(target);
        }
        
        // View mode toggles
        else if (target.name === 'viewMode') {
            this.toggleViewMode(target);
        }
    }

    async updateJobStatus(jobId, status, notes = '') {
        try {
            const formData = new FormData();
            formData.append('call_id', jobId);
            formData.append('status', status);
            formData.append('notes', notes);
            formData.append('csrf_token', this.getCSRFToken());

            const response = await fetch('/job/update-status', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showNotification(`Job status updated to ${status.replace('_', ' ')}`, 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                throw new Error('Failed to update job status');
            }
        } catch (error) {
            this.showNotification('Failed to update job status', 'error');
            console.error('Error updating job status:', error);
        }
    }

    filterJobs(filterInput) {
        const filter = filterInput.id.replace(/^(filter|admin)/, '').toLowerCase();
        const jobCards = document.querySelectorAll('.job-card');
        const jobRows = document.querySelectorAll('.admin-job-row');
        
        [...jobCards, ...jobRows].forEach(element => {
            const elementStatus = element.dataset.status;
            let show = false;
            
            if (filter === 'all') {
                show = true;
            } else if (filter === 'progress' && elementStatus === 'in_progress') {
                show = true;
            } else if (filter === elementStatus) {
                show = true;
            }
            
            element.style.display = show ? '' : 'none';
        });
        
        this.updateFilterCounts();
    }

    toggleViewMode(input) {
        const cardsContainer = document.getElementById('cardsContainer');
        const tableContainer = document.getElementById('tableContainer');
        
        if (input.id === 'cardView') {
            cardsContainer.style.display = '';
            tableContainer.style.display = 'none';
        } else {
            cardsContainer.style.display = 'none';
            tableContainer.style.display = '';
        }
        
        // Save preference
        localStorage.setItem('dashboardViewMode', input.id);
    }

    setupFileUpload() {
        const uploadAreas = document.querySelectorAll('.upload-area');
        
        uploadAreas.forEach(area => {
            area.addEventListener('dragover', this.handleDragOver.bind(this));
            area.addEventListener('dragleave', this.handleDragLeave.bind(this));
            area.addEventListener('drop', this.handleDrop.bind(this));
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        this.handleFiles(files, e.currentTarget);
    }

    handleFiles(files, uploadArea) {
        const fileInput = uploadArea.querySelector('input[type="file"]');
        const filePreview = uploadArea.parentNode.querySelector('.file-preview');
        
        if (fileInput && filePreview) {
            // Update file input
            const dataTransfer = new DataTransfer();
            files.forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;
            
            // Update preview
            this.updateFilePreview(files, filePreview);
        }
    }

    updateFilePreview(files, container) {
        container.innerHTML = '';
        
        files.forEach((file, index) => {
            const fileItem = this.createFilePreviewItem(file, index);
            container.appendChild(fileItem);
        });
    }

    createFilePreviewItem(file, index) {
        const item = document.createElement('div');
        item.className = 'file-item';
        
        const icon = this.getFileIcon(file.name);
        const size = this.formatFileSize(file.size);
        
        item.innerHTML = `
            <div class="file-icon">
                <i class="${icon}"></i>
            </div>
            <div class="file-info">
                <p class="file-name">${file.name}</p>
                <p class="file-size">${size}</p>
            </div>
            <button type="button" class="file-remove" onclick="this.parentNode.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        return item;
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        
        if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
            return 'fas fa-image';
        } else if (ext === 'pdf') {
            return 'fas fa-file-pdf';
        } else if (['doc', 'docx'].includes(ext)) {
            return 'fas fa-file-word';
        } else if (['mp4', 'mov', 'avi'].includes(ext)) {
            return 'fas fa-video';
        }
        return 'fas fa-file';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    triggerFileUpload(jobId) {
        // Create dynamic file input for job-specific uploads
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = 'image/*,video/*,.pdf,.doc,.docx';
        
        input.onchange = (e) => {
            const files = Array.from(e.target.files);
            this.uploadJobFiles(jobId, files);
        };
        
        input.click();
    }

    triggerCameraCapture(jobId) {
        // Mobile camera capture
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.capture = 'environment'; // Use back camera
        
        input.onchange = (e) => {
            const files = Array.from(e.target.files);
            this.uploadJobFiles(jobId, files);
        };
        
        input.click();
    }

    async uploadJobFiles(jobId, files) {
        if (files.length === 0) return;
        
        const formData = new FormData();
        formData.append('call_id', jobId);
        formData.append('csrf_token', this.getCSRFToken());
        
        files.forEach(file => {
            formData.append('files', file);
        });
        
        try {
            this.showNotification('Uploading files...', 'info');
            
            const response = await fetch('/job/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                this.showNotification(`Uploaded ${files.length} file(s)`, 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            this.showNotification('Failed to upload files', 'error');
            console.error('Upload error:', error);
        }
    }

    toggleToolieChat() {
        // Integration with existing Toolie chat system
        const chatWidget = document.getElementById('chat-widget');
        const toolieBubble = document.querySelector('.toolie-bubble');
        
        if (chatWidget) {
            const isVisible = chatWidget.style.display !== 'none';
            chatWidget.style.display = isVisible ? 'none' : 'block';
            
            // Toggle bubble animation
            if (isVisible) {
                toolieBubble.classList.remove('pulse');
            } else {
                toolieBubble.classList.add('pulse');
            }
        } else {
            // Fallback: show Toolie modal or redirect
            this.showToolieModal();
        }
    }

    showToolieModal() {
        // Create dynamic Toolie modal if chat widget not available
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-robot me-2"></i>
                            Toolie Assistant
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Toolie can help you with:</p>
                        <ul>
                            <li>Finding electrical parts and specifications</li>
                            <li>Troubleshooting electrical issues</li>
                            <li>Code calculations and estimates</li>
                            <li>Safety guidelines and best practices</li>
                        </ul>
                        <div class="d-grid gap-2">
                            <a href="/troubleshooting" class="btn btn-primary">
                                <i class="fas fa-tools me-2"></i>
                                Start Troubleshooting
                            </a>
                            <a href="/quote_estimator" class="btn btn-outline-primary">
                                <i class="fas fa-calculator me-2"></i>
                                Get Quote Estimate
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
        
        // Remove modal after hiding
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    setupFormHandlers() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                }
            });
        });
    }

    setupMobileHandlers() {
        // Add mobile-specific touch handlers
        if ('ontouchstart' in window) {
            // Add touch feedback for buttons
            document.addEventListener('touchstart', (e) => {
                if (e.target.matches('.btn-modern')) {
                    e.target.style.transform = 'scale(0.98)';
                }
            });
            
            document.addEventListener('touchend', (e) => {
                if (e.target.matches('.btn-modern')) {
                    setTimeout(() => {
                        e.target.style.transform = '';
                    }, 100);
                }
            });
        }
    }

    setupRealTimeUpdates() {
        // Periodic refresh for admin dashboard
        if (window.location.pathname.includes('admin')) {
            setInterval(() => {
                this.refreshStats();
            }, 30000); // Refresh every 30 seconds
        }
    }

    async refreshStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatCards(stats);
            }
        } catch (error) {
            console.log('Stats refresh failed:', error);
        }
    }

    updateStatCards(stats) {
        const statCards = document.querySelectorAll('.stat-card h3');
        if (stats && statCards.length > 0) {
            // Update stat numbers with animation
            statCards.forEach((card, index) => {
                if (stats[index] !== undefined) {
                    this.animateCounter(card, parseInt(card.textContent), stats[index]);
                }
            });
        }
    }

    animateCounter(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };
        
        requestAnimationFrame(updateCounter);
    }

    updateFilterCounts() {
        // Update filter labels with counts
        const filters = document.querySelectorAll('input[name*="Filter"]');
        
        filters.forEach(filter => {
            const label = document.querySelector(`label[for="${filter.id}"]`);
            if (label) {
                const baseText = label.textContent.split(' (')[0];
                const count = this.getFilterCount(filter.id);
                label.textContent = count > 0 ? `${baseText} (${count})` : baseText;
            }
        });
    }

    getFilterCount(filterId) {
        const filter = filterId.replace(/^(filter|admin)/, '').toLowerCase();
        const elements = document.querySelectorAll('.job-card, .admin-job-row');
        
        if (filter === 'all') return elements.length;
        
        return Array.from(elements).filter(el => {
            const status = el.dataset.status;
            return filter === 'progress' ? status === 'in_progress' : status === filter;
        }).length;
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.style.minWidth = '300px';
        
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentNode.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    getCSRFToken() {
        const tokenInput = document.querySelector('input[name="csrf_token"]');
        return tokenInput ? tokenInput.value : '';
    }

    initializeComponents() {
        // Restore saved view mode
        const savedViewMode = localStorage.getItem('dashboardViewMode');
        if (savedViewMode) {
            const input = document.getElementById(savedViewMode);
            if (input) {
                input.checked = true;
                this.toggleViewMode(input);
            }
        }
        
        // Initialize filter counts
        this.updateFilterCounts();
        
        // Setup periodic updates for mobile
        if (window.innerWidth <= 768) {
            // Pull to refresh simulation
            let startY = 0;
            
            document.addEventListener('touchstart', (e) => {
                startY = e.touches[0].clientY;
            });
            
            document.addEventListener('touchmove', (e) => {
                const currentY = e.touches[0].clientY;
                const deltaY = currentY - startY;
                
                if (deltaY > 100 && window.scrollY === 0) {
                    this.showNotification('Release to refresh', 'info');
                }
            });
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new KynetikDashboard();
});

// Export for external use
window.KynetikDashboard = KynetikDashboard;