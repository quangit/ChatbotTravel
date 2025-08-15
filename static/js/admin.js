class AdminInterface {
    constructor() {
        this.uploadForm = document.getElementById('uploadForm');
        this.fileInput = document.getElementById('fileInput');
        this.uploadButton = document.getElementById('uploadButton');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.uploadStatus = document.getElementById('uploadStatus');
        this.statusMessage = document.getElementById('statusMessage');
        this.uploadProgress = document.getElementById('uploadProgress');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // File selection
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Form submission
        this.uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        
        // Drag and drop support
        const fileInputLabel = this.fileInput.nextElementSibling;
        
        fileInputLabel.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileInputLabel.style.borderColor = '#4facfe';
            fileInputLabel.style.background = '#f0f8ff';
        });
        
        fileInputLabel.addEventListener('dragleave', (e) => {
            e.preventDefault();
            fileInputLabel.style.borderColor = '#ccc';
            fileInputLabel.style.background = 'white';
        });
        
        fileInputLabel.addEventListener('drop', (e) => {
            e.preventDefault();
            fileInputLabel.style.borderColor = '#ccc';
            fileInputLabel.style.background = 'white';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.fileInput.files = files;
                this.handleFileSelect({ target: { files: files } });
            }
        });
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        
        if (!file) {
            this.hideFileInfo();
            this.uploadButton.disabled = true;
            return;
        }
        
        // Validate file type
        const allowedExtensions = ['txt', 'pdf', 'docx'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        if (!allowedExtensions.includes(fileExtension)) {
            this.showStatus('error', 'Định dạng file không được hỗ trợ. Vui lòng chọn file .txt, .pdf hoặc .docx');
            this.hideFileInfo();
            this.uploadButton.disabled = true;
            return;
        }
        
        // Validate file size (16MB limit)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            this.showStatus('error', 'Kích thước file vượt quá giới hạn 16MB');
            this.hideFileInfo();
            this.uploadButton.disabled = true;
            return;
        }
        
        // Show file info
        this.showFileInfo(file);
        this.uploadButton.disabled = false;
        this.hideStatus();
    }
    
    showFileInfo(file) {
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.fileInfo.style.display = 'block';
    }
    
    hideFileInfo() {
        this.fileInfo.style.display = 'none';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async handleUpload(event) {
        event.preventDefault();
        
        const file = this.fileInput.files[0];
        if (!file) {
            this.showStatus('error', 'Vui lòng chọn một file để tải lên');
            return;
        }
        
        // Show progress
        this.showProgress();
        this.uploadButton.disabled = true;
        this.hideStatus();
        
        try {
            // Create FormData
            const formData = new FormData();
            formData.append('file', file);
            
            // Upload file
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showStatus('success', data.message);
                this.resetForm();
            } else {
                this.showStatus('error', data.error || 'Có lỗi xảy ra trong quá trình xử lý file');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showStatus('error', 'Không thể kết nối đến máy chủ. Vui lòng thử lại.');
        } finally {
            this.hideProgress();
            this.uploadButton.disabled = false;
        }
    }
    
    showProgress() {
        this.uploadProgress.style.display = 'block';
        
        // Animate progress bar
        const progressFill = this.uploadProgress.querySelector('.progress-fill');
        progressFill.style.width = '0%';
        
        // Simulate progress animation
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            progressFill.style.width = progress + '%';
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
        
        // Store interval ID to clear it later
        this.progressInterval = interval;
    }
    
    hideProgress() {
        this.uploadProgress.style.display = 'none';
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        // Reset progress bar
        const progressFill = this.uploadProgress.querySelector('.progress-fill');
        progressFill.style.width = '0%';
    }
    
    showStatus(type, message) {
        this.uploadStatus.className = `upload-status ${type === 'error' ? 'error' : ''}`;
        this.statusMessage.textContent = message;
        this.uploadStatus.style.display = 'block';
        
        // Auto hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.hideStatus();
            }, 5000);
        }
    }
    
    hideStatus() {
        this.uploadStatus.style.display = 'none';
    }
    
    resetForm() {
        this.fileInput.value = '';
        this.hideFileInfo();
        this.uploadButton.disabled = true;
        
        // Reset file input label
        const label = this.fileInput.nextElementSibling;
        const span = label.querySelector('span');
        span.textContent = 'Chọn tệp tin';
        
        label.style.borderColor = '#ccc';
        label.style.background = 'white';
    }
}

// Initialize admin interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on the admin page
    if (document.getElementById('uploadForm')) {
        new AdminInterface();
    }
});
