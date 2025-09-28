const API_BASE = 'http://localhost:5000/api/v1';

class PolisAPI {
    static async getLegislation(status = 'active', page = 1) {
        const response = await fetch(`${API_BASE}/legislation?status=${status}&page=${page}`);
        if (!response.ok) throw new Error('Failed to fetch legislation');
        return await response.json();
    }

    static async getLegislationDetail(id) {
        const response = await fetch(`${API_BASE}/legislation/${id}`);
        if (!response.ok) throw new Error('Failed to fetch legislation details');
        return await response.json();
    }

    static async submitFeedback(feedbackData) {
        const response = await fetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(feedbackData)
        });
        if (!response.ok) throw new Error('Failed to submit feedback');
        return await response.json();
    }

    static async getCivicPulse(legislationId) {
        const response = await fetch(`${API_BASE}/civic-pulse/${legislationId}`);
        if (!response.ok) throw new Error('Failed to fetch civic pulse data');
        return await response.json();
    }
}