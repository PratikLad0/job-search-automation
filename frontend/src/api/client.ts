import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const jobsApi = {
    list: async (params?: any) => {
        const response = await api.get('/jobs', { params });
        return response.data;
    },
    get: async (id: number) => {
        const response = await api.get(`/jobs/${id}`);
        return response.data;
    },
    markApplied: async (id: number) => {
        const response = await api.post(`/jobs/${id}/applied`);
        return response.data;
    },
    generateDocs: async (id: number) => {
        const response = await api.post(`/generate/${id}`);
        return response.data;
    },
};

export const statsApi = {
    get: async () => {
        const response = await api.get('/stats');
        return response.data;
    },
};
