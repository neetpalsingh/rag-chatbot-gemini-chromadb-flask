class ChatApp {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.chatContainer = document.getElementById('chatContainer');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.statsText = document.getElementById('statsText');
        this.uploadStatus = document.getElementById('uploadStatus');
        this.loader = document.getElementById('loader');
        this.toast = document.getElementById('toast');

        this.initializeEventListeners();
        this.loadStats();
    }

    initializeEventListeners() {
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        this.sendBtn.addEventListener('click', () => this.handleSendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSendMessage();
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.uploadFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        if (!this.validateFile(file)) return;

        this.showLoader();
        this.hideUploadStatus();

        try {
            const response = await apiClient.uploadDocument(file);
            
            if (response.success) {
                this.showUploadStatus('success', 
                    `✅ ${response.data.filename} uploaded (${response.data.chunks_count} chunks)`
                );
                this.showToast('success', 'Document uploaded successfully!');
                await this.loadStats();
            } else {
                this.showUploadStatus('error', `❌ ${response.error}`);
                this.showToast('error', response.error);
            }
        } catch (error) {
            this.showUploadStatus('error', '❌ Upload failed');
            this.showToast('error', 'Failed to upload document');
            console.error('Upload error:', error);
        } finally {
            this.hideLoader();
            this.fileInput.value = '';
        }
    }

    validateFile(file) {
        const validTypes = ['application/pdf', 'text/plain'];
        const maxSize = 10 * 1024 * 1024;

        if (!validTypes.includes(file.type)) {
            this.showToast('error', 'Only PDF and TXT files are allowed');
            return false;
        }

        if (file.size > maxSize) {
            this.showToast('error', 'File size must be less than 10MB');
            return false;
        }

        return true;
    }

    async handleSendMessage() {
        const query = this.chatInput.value.trim();
        if (!query) return;

        this.addMessage('user', query);
        this.chatInput.value = '';
        this.sendBtn.disabled = true;

        this.showLoader();

        try {
            const response = await apiClient.queryDocument(query);

            if (response.success) {
                this.addMessage('bot', response.data.answer, response.data.sources);
            } else {
                this.addMessage('bot', `Error: ${response.error}`);
                this.showToast('error', response.error);
            }
        } catch (error) {
            this.addMessage('bot', 'Sorry, something went wrong. Please try again.');
            this.showToast('error', 'Query failed');
            console.error('Query error:', error);
        } finally {
            this.hideLoader();
            this.sendBtn.disabled = false;
        }
    }

    addMessage(role, content, sources = []) {
        const welcomeMsg = this.chatContainer.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;

        if (sources && sources.length > 0) {
            const sourcesDiv = this.createSourcesElement(sources);
            bubbleDiv.appendChild(sourcesDiv);
        }

        messageDiv.appendChild(bubbleDiv);
        this.chatContainer.appendChild(messageDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    createSourcesElement(sources) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'sources';
        
        const title = document.createElement('div');
        title.className = 'sources-title';
        title.textContent = `📚 Sources (${sources.length}):`;
        sourcesDiv.appendChild(title);

        sources.forEach((source, idx) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.textContent = `${idx + 1}. ${source.metadata.filename} - Chunk ${source.metadata.chunk_index + 1}`;
            sourceItem.title = source.text.substring(0, 200) + '...';
            sourcesDiv.appendChild(sourceItem);
        });

        return sourcesDiv;
    }

    async loadStats() {
        try {
            const response = await apiClient.getStats();
            if (response.success) {
                this.statsText.innerHTML = `Total chunks: <strong>${response.data.total_chunks}</strong>`;
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    showUploadStatus(type, message) {
        this.uploadStatus.className = `upload-status ${type}`;
        this.uploadStatus.textContent = message;
    }

    hideUploadStatus() {
        this.uploadStatus.className = 'upload-status';
        this.uploadStatus.textContent = '';
    }

    showLoader() {
        this.loader.classList.remove('hidden');
    }

    hideLoader() {
        this.loader.classList.add('hidden');
    }

    showToast(type, message) {
        this.toast.textContent = message;
        this.toast.className = `toast ${type} show`;

        setTimeout(() => {
            this.toast.classList.remove('show');
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

