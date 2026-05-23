import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (username: string, email: string, password: string) =>
    api.post('/auth/register', { username, email, password }),

  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),

  getMe: () => api.get('/auth/me'),
};

// Prediction API
export const predictAPI = {
  predict: (imageBase64: string) =>
    api.post('/predict', { image: imageBase64 }),
};

// History API
export const historyAPI = {
  getHistory: () => api.get('/history'),
};

// Categories API
export const categoriesAPI = {
  getCategories: () => api.get('/categories'),
};

export default api;
