class DocumentManager {
    constructor() {
        this.uploadDocBtn = document.getElementById('uploadDocBtn');
        this.uploadModal = document.getElementById('uploadModal');
        this.modalCloseBtn = document.getElementById('modalCloseBtn');
        this.categorySelect = document.getElementById('categorySelect');
        this.fileUploadArea = document.getElementById('fileUploadArea');
        this.docFileInput = document.getElementById('docFileInput');
        this.selectedFileName = document.getElementById('selectedFileName');
        this.cancelUploadBtn = document.getElementById('cancelUploadBtn');
        this.confirmUploadBtn = document.getElementById('confirmUploadBtn');
        this.documentsTableBody = document.getElementById('documentsTableBody');
        this.loader = document.getElementById('loader');
        this.toast = document.getElementById('toast');

        this.selectedFile = null;

        this.initializeEventListeners();
        this.loadDocuments();
    }

    initializeEventListeners() {
        this.uploadDocBtn.addEventListener('click', () => this.openUploadModal());
        this.modalCloseBtn.addEventListener('click', () => this.closeUploadModal());
        this.cancelUploadBtn.addEventListener('click', () => this.closeUploadModal());
        this.confirmUploadBtn.addEventListener('click', () => this.handleUpload());

        this.fileUploadArea.addEventListener('click', () => this.docFileInput.click());
        this.docFileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        this.fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.fileUploadArea.style.borderColor = 'var(--primary-color)';
        });

        this.fileUploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.fileUploadArea.style.borderColor = 'var(--border-color)';
        });

        this.fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.fileUploadArea.style.borderColor = 'var(--border-color)';
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.selectFile(files[0]);
            }
        });
    }

    openUploadModal() {
        this.uploadModal.classList.remove('hidden');
        this.selectedFile = null;
        this.selectedFileName.textContent = '';
        this.confirmUploadBtn.disabled = true;
    }

    closeUploadModal() {
        this.uploadModal.classList.add('hidden');
        this.docFileInput.value = '';
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.selectFile(file);
        }
    }

    selectFile(file) {
        const validTypes = ['application/pdf', 'text/plain'];
        const maxSize = 10 * 1024 * 1024;

        if (!validTypes.includes(file.type)) {
            this.showToast('error', 'Only PDF and TXT files are allowed');
            return;
        }

        if (file.size > maxSize) {
            this.showToast('error', 'File size must be less than 10MB');
            return;
        }

        this.selectedFile = file;
        this.selectedFileName.innerHTML = `<i class="fas fa-file"></i> ${file.name} (${this.formatFileSize(file.size)})`;
        this.confirmUploadBtn.disabled = false;
    }

    async handleUpload() {
        if (!this.selectedFile) return;

        const category = this.categorySelect.value;

        this.showLoader();
        this.closeUploadModal();

        try {
            const response = await apiClient.uploadDocument(this.selectedFile, category);
            
            if (response.success) {
                this.showToast('success', 'Document uploaded successfully');
                await this.loadDocuments();
            } else {
                this.showToast('error', response.error);
            }
        } catch (error) {
            this.showToast('error', 'Failed to upload document');
            console.error('Upload error:', error);
        } finally {
            this.hideLoader();
        }
    }

    async loadDocuments() {
        this.showLoader();

        try {
            const response = await apiClient.getDocuments();
            
            if (response.success) {
                this.renderDocuments(response.data);
            } else {
                this.showToast('error', 'Failed to load documents');
            }
        } catch (error) {
            console.error('Load documents error:', error);
            this.showToast('error', 'Failed to load documents');
        } finally {
            this.hideLoader();
        }
    }

    renderDocuments(documents) {
        if (!documents || documents.length === 0) {
            this.documentsTableBody.innerHTML = `
                <tr class="empty-state">
                    <td colspan="8">
                        <i class="fas fa-folder-open"></i>
                        <p>No documents uploaded yet</p>
                    </td>
                </tr>
            `;
            return;
        }

        this.documentsTableBody.innerHTML = documents.map(doc => `
            <tr>
                <td><i class="fas fa-file-${doc.file_type === 'pdf' ? 'pdf' : 'alt'}"></i> ${doc.filename}</td>
                <td><span class="badge" style="background: #e0e7ff; color: #3730a3;">${doc.category.toUpperCase()}</span></td>
                <td>${doc.file_type.toUpperCase()}</td>
                <td>${this.formatFileSize(doc.file_size)}</td>
                <td>${doc.chunks_count}</td>
                <td><span class="badge ${doc.status === 'processed' ? 'success' : 'processing'}">${doc.status.toUpperCase()}</span></td>
                <td>${this.formatDate(doc.uploaded_at)}</td>
                <td>
                    <button class="action-btn delete" onclick="documentManager.deleteDocument('${doc.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) return;

        this.showLoader();

        try {
            const response = await apiClient.deleteDocument(docId);
            
            if (response.success) {
                this.showToast('success', 'Document deleted successfully');
                await this.loadDocuments();
            } else {
                this.showToast('error', response.error);
            }
        } catch (error) {
            this.showToast('error', 'Failed to delete document');
            console.error('Delete error:', error);
        } finally {
            this.hideLoader();
        }
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return 'Today';
        if (days === 1) return 'Yesterday';
        if (days < 7) return days + ' days ago';
        return date.toLocaleDateString();
    }

    showLoader() {
        this.loader.classList.remove('hidden');
    }

    hideLoader() {
        this.loader.classList.add('hidden');
    }

    showToast(type, message) {
        this.toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
        this.toast.className = `toast ${type} show`;

        setTimeout(() => {
            this.toast.classList.remove('show');
        }, 3000);
    }
}

let documentManager;
document.addEventListener('DOMContentLoaded', () => {
    documentManager = new DocumentManager();
});
