import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const uploadFile = (formData) => {
    return api.post('/api/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    }).then(res => res.data);
};

export const getFiles = () => {
    return api.get('/api/files').then(res => res.data);
};

export const submitQuery = (formData) => {
    return api.post('/api/query', formData).then(res => res.data);
};

export default api;