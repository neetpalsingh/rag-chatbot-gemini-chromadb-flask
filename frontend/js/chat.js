class ChatInterface {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.attachBtn = document.getElementById('attachBtn');
        this.fileInput = document.getElementById('fileInput');
        this.loader = document.getElementById('loader');
        this.toast = document.getElementById('toast');
        this.newChatBtn = document.getElementById('newChatBtn');

        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettingsBtn = document.getElementById('closeSettingsBtn');
        this.saveSettingsBtn = document.getElementById('saveSettingsBtn');
        this.resetSettingsBtn = document.getElementById('resetSettingsBtn');

        this.topKSlider = document.getElementById('topKSlider');
        this.topKValue = document.getElementById('topKValue');
        this.temperatureSlider = document.getElementById('temperatureSlider');
        this.temperatureValue = document.getElementById('temperatureValue');
        this.topPSlider = document.getElementById('topPSlider');
        this.topPValue = document.getElementById('topPValue');

        this.settings = this.loadSettings();

        this.initializeEventListeners();
        this.updateSettingsUI();
    }

    loadSettings() {
        const saved = localStorage.getItem('llm_settings');
        return saved ? JSON.parse(saved) : {
            topK: 5,
            temperature: 0.7,
            topP: 0.95
        };
    }

    saveSettings() {
        localStorage.setItem('llm_settings', JSON.stringify(this.settings));
    }

    updateSettingsUI() {
        this.topKSlider.value = this.settings.topK;
        this.topKValue.textContent = this.settings.topK;
        this.temperatureSlider.value = this.settings.temperature;
        this.temperatureValue.textContent = this.settings.temperature;
        this.topPSlider.value = this.settings.topP;
        this.topPValue.textContent = this.settings.topP;
    }

    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.handleSendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        this.attachBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));

        if (this.newChatBtn) {
            this.newChatBtn.addEventListener('click', () => this.handleNewChat());
        }

        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.handleSaveSettings());
        this.resetSettingsBtn.addEventListener('click', () => this.handleResetSettings());

        this.topKSlider.addEventListener('input', (e) => {
            this.topKValue.textContent = e.target.value;
        });

        this.temperatureSlider.addEventListener('input', (e) => {
            this.temperatureValue.textContent = e.target.value;
        });

        this.topPSlider.addEventListener('input', (e) => {
            this.topPValue.textContent = e.target.value;
        });

        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettings();
            }
        });
    }

    openSettings() {
        this.updateSettingsUI();
        this.settingsModal.classList.remove('hidden');
    }

    closeSettings() {
        this.settingsModal.classList.add('hidden');
    }

    handleSaveSettings() {
        this.settings.topK = parseInt(this.topKSlider.value);
        this.settings.temperature = parseFloat(this.temperatureSlider.value);
        this.settings.topP = parseFloat(this.topPSlider.value);
        this.saveSettings();
        this.closeSettings();
        this.showToast('success', 'Settings saved successfully');
    }

    handleResetSettings() {
        this.settings = {
            topK: 5,
            temperature: 0.7,
            topP: 0.95
        };
        this.updateSettingsUI();
        this.saveSettings();
        this.showToast('success', 'Settings reset to defaults');
    }

    async handleSendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage('user', message);
        this.messageInput.value = '';
        this.sendBtn.disabled = true;

        this.showLoader();

        try {
            const response = await apiClient.queryDocument(message, this.settings);

            if (response.success) {
                this.addMessage('bot', response.data.answer, response.data.metadata);
            } else {
                this.addMessage('bot', `Error: ${response.error}`);
                this.showToast('error', response.error);
            }
        } catch (error) {
            this.addMessage('bot', error.message || 'Sorry, something went wrong. Please try again.');
            this.showToast('error', error.message || 'Query failed');
            console.error('Query error:', error);
        } finally {
            this.hideLoader();
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }
    }

    async handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        if (!this.validateFile(file)) {
            e.target.value = '';
            return;
        }

        this.showLoader();

        try {
            // Always use general category for chat uploads
            const response = await apiClient.uploadDocument(file, 'general');

            if (response.success) {
                this.showToast('success', `Document uploaded: ${response.data.chunks_count} chunks`);
                this.addMessage('bot', `Document "${response.data.filename}" uploaded successfully with ${response.data.chunks_count} chunks.`);
            } else {
                this.showToast('error', response.error);
            }
        } catch (error) {
            this.showToast('error', 'Failed to upload document');
            console.error('Upload error:', error);
        } finally {
            this.hideLoader();
            e.target.value = '';
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

    addMessage(role, content, metadata = null) {
        const welcomeMsg = this.chatContainer.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();

        const messageGroup = document.createElement('div');
        messageGroup.className = `message-group ${role}`;

        const avatar = document.createElement('div');
        avatar.className = `avatar ${role}`;
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const label = document.createElement('div');
        label.className = 'message-label';
        label.textContent = role === 'user' ? 'You' : 'AssistantBot';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        if (role === 'bot') {
            bubble.innerHTML = this.formatMarkdown(content);
        } else {
            bubble.textContent = content;
        }

        if (role === 'bot' && metadata) {
            const footer = this.createMessageFooter(metadata);
            if (footer) {
                bubble.appendChild(footer);
            }
        }

        messageContent.appendChild(label);
        messageContent.appendChild(bubble);
        messageGroup.appendChild(avatar);
        messageGroup.appendChild(messageContent);

        this.chatContainer.appendChild(messageGroup);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    formatMarkdown(text) {
        if (!text) return '';

        let html = text;

        // Convert **bold** to <strong>
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Convert *italic* to <em>
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Convert numbered lists (1., 2., etc.)
        html = html.replace(/^(\d+)\.\s+\*\*(.*?)\*\*/gm, '<div class="numbered-item"><span class="number">$1.</span><strong>$2</strong></div>');

        // Convert bullet points with sub-bullets
        html = html.replace(/^\s{4}\*\s+(.*?)$/gm, '<div class="sub-bullet">• $1</div>');

        // Convert paragraphs
        html = html.replace(/\n\n/g, '<br><br>');
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    createMessageFooter(metadata) {
        if (!metadata) return null;

        const footer = document.createElement('div');
        footer.className = 'message-footer';
        footer.style.marginTop = '0.75rem';
        footer.style.paddingTop = '0.75rem';
        footer.style.borderTop = '1px solid rgba(0,0,0,0.1)';
        footer.style.fontSize = '11px';
        footer.style.display = 'flex';
        footer.style.flexWrap = 'wrap';
        footer.style.gap = '1rem';
        footer.style.opacity = '0.85';

        const hasMemory = metadata.conversation_history && metadata.conversation_history.length > 0;
        const hasDocuments = metadata.used_documents && metadata.used_documents.length > 0;

        if (hasMemory) {
            const memoryDiv = document.createElement('div');
            memoryDiv.style.display = 'flex';
            memoryDiv.style.alignItems = 'center';
            memoryDiv.style.gap = '0.5rem';
            memoryDiv.style.color = '#6b7280';
            memoryDiv.innerHTML = `
                <i class="fas fa-brain" style="color: #8b5cf6;"></i>
                <span>Memory: ${metadata.conversation_history.length} message${metadata.conversation_history.length > 1 ? 's' : ''} in context</span>
            `;
            footer.appendChild(memoryDiv);
        }

        if (hasDocuments) {
            const docsDiv = document.createElement('div');
            docsDiv.style.display = 'flex';
            docsDiv.style.alignItems = 'center';
            docsDiv.style.gap = '0.5rem';
            docsDiv.style.color = '#6b7280';

            const docNames = metadata.used_documents.join(', ');

            docsDiv.innerHTML = `
                <i class="fas fa-file-alt" style="color: #3b82f6;"></i>
                <span title="${docNames}">Documents: ${docNames}</span>
            `;
            footer.appendChild(docsDiv);
        }

        return footer.children.length > 0 ? footer : null;
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

    async handleNewChat() {
        if (confirm('Start a new chat? Current conversation will be cleared.')) {
            try {
                this.showLoader();

                await apiClient.clearSession();

                this.chatContainer.innerHTML = `
                    <div class="welcome-message">
                        <i class="fas fa-robot"></i>
                        <h2>Welcome to Web Chat</h2>
                        <p>Upload documents and start asking questions!</p>
                    </div>
                `;

                this.showToast('success', 'New chat started');
            } catch (error) {
                this.showToast('error', 'Failed to start new chat');
                console.error('New chat error:', error);
            } finally {
                this.hideLoader();
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});
