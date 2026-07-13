const API_BASE_URL = 'http://localhost:8000/api';

class ApiClient {
    constructor() {
        this.sessionId = this._getOrCreateSessionId();
    }

    _getOrCreateSessionId() {
        let sessionId = localStorage.getItem('chat_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(7);
            localStorage.setItem('chat_session_id', sessionId);
        }
        return sessionId;
    }

    async clearSession() {
        const response = await fetch(`${API_BASE_URL}/clear/${this.sessionId}`, {
            method: 'POST'
        });

        if (response.ok) {
            localStorage.removeItem('chat_session_id');
            this.sessionId = this._getOrCreateSessionId();
        }

        return await response.json();
    }

    async uploadDocument(file, category = 'general') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', category);

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return await response.json();
    }

    async queryDocument(query, settings = {}) {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                session_id: this.sessionId,
                top_k: settings.topK || 5,
                temperature: settings.temperature || 0.7,
                top_p: settings.topP || 0.95
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }

        return await response.json();
    }

    async getDocuments() {
        const response = await fetch(`${API_BASE_URL}/documents`);
        return await response.json();
    }

    async deleteDocument(docId) {
        const response = await fetch(`${API_BASE_URL}/documents/${docId}`, {
            method: 'DELETE'
        });
        return await response.json();
    }

    async getStats() {
        const response = await fetch(`${API_BASE_URL}/stats`);
        return await response.json();
    }

    async healthCheck() {
        const response = await fetch(`${API_BASE_URL}/health`);
        return await response.json();
    }
}

const apiClient = new ApiClient();
