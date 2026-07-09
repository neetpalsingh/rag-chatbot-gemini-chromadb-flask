const API_BASE_URL = 'http://localhost:5000/api';

class ApiClient {
    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        return await response.json();
    }

    async queryDocument(query) {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
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
