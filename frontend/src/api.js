import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Mission endpoints
export const missionsApi = {
    // Upload file (PDF or CSV)
    uploadFile: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/api/missions/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    // Submit text
    submitText: async (content, sourceLabel = 'text_input') => {
        const response = await api.post('/api/missions/text', {
            content,
            source_label: sourceLabel,
        });
        return response.data;
    },

    // Get all missions
    getAll: async (limit = 100, offset = 0) => {
        const response = await api.get('/api/missions', {
            params: { limit, offset },
        });
        return response.data;
    },

    // Get mission by ID
    getById: async (missionId) => {
        const response = await api.get(`/api/missions/${missionId}`);
        return response.data;
    },

    // Delete mission
    delete: async (missionId) => {
        const response = await api.delete(`/api/missions/${missionId}`);
        return response.data;
    },
};

// Analysis endpoints
export const analysisApi = {
    // Execute analysis
    execute: async (missionId, useRag = true) => {
        const response = await api.post(`/api/analysis/${missionId}`, {
            use_rag: useRag,
        });
        return response.data;
    },

    // Get analysis result
    getResult: async (missionId) => {
        const response = await api.get(`/api/analysis/${missionId}`);
        return response.data;
    },

    // Get analysis history
    getHistory: async (missionId) => {
        const response = await api.get(`/api/analysis/${missionId}/history`);
        return response.data;
    },
};

// Review endpoints
export const reviewsApi = {
    // Submit or update review
    submit: async (missionId, analystNotes, approved) => {
        const response = await api.post(`/api/reviews/${missionId}`, {
            analyst_notes: analystNotes,
            approved,
        });
        return response.data;
    },

    // Get review
    get: async (missionId) => {
        const response = await api.get(`/api/reviews/${missionId}`);
        return response.data;
    },
};

// Health check
export const healthCheck = async () => {
    const response = await api.get('/health');
    return response.data;
};

// Analytics endpoints
export const analyticsApi = {
    // Get summary statistics
    getSummary: async () => {
        const response = await api.get('/api/analytics/summary');
        return response.data;
    },

    // Get risk distribution
    getRiskDistribution: async () => {
        const response = await api.get('/api/analytics/risk-distribution');
        return response.data;
    },

    // Get trends over time
    getTrends: async (days = 30) => {
        const response = await api.get('/api/analytics/trends', {
            params: { days },
        });
        return response.data;
    },

    // Get entity type breakdown
    getEntityBreakdown: async () => {
        const response = await api.get('/api/analytics/entity-breakdown');
        return response.data;
    },

    // Get review status counts
    getReviewStatus: async () => {
        const response = await api.get('/api/analytics/review-status');
        return response.data;
    },

    // Get high risk missions
    getHighRiskMissions: async (limit = 5) => {
        const response = await api.get('/api/analytics/high-risk-missions', {
            params: { limit },
        });
        return response.data;
    },
};

export default api;
