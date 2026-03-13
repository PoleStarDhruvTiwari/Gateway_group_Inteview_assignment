import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const authApi = axios.create({
    baseURL: API_URL,
});

export const login = (data) => {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    return authApi.post('/api/auth/token', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    }).then(res => res.data);
};

export const register = (data) => {
    return authApi.post('/api/auth/register', data).then(res => res.data);
};

export const getCurrentUser = () => {
    const token = localStorage.getItem('token');
    if (!token) return Promise.reject('No token');
    
    return authApi.get('/api/auth/me', {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    }).then(res => res.data);
};

export const logout = () => {
    localStorage.removeItem('token');
};