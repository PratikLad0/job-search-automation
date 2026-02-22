import axios from 'axios';
import { API_BASE_URL } from '../config';

export const api = axios.create({
    baseURL: API_BASE_URL,
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
        const response = await api.post(`/generators/${id}`);
        return response.data;
    },
};

export const statsApi = {
    get: async () => {
        const response = await api.get('/stats');
        return response.data;
    },
};

export const emailsApi = {
    list: async (skip: number = 0, limit: number = 50) => {
        const response = await api.get(`/emails/?skip=${skip}&limit=${limit}`);
        return response.data;
    },
    get: async (id: number) => {
        const response = await api.get(`/emails/${id}`);
        return response.data;
    },
    reply: async (id: number) => {
        const response = await api.post(`/emails/${id}/reply`);
        return response.data;
    }
};
