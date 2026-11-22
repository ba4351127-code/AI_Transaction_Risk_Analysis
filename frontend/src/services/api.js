import axios from 'axios';

// Central Axios instance connecting to FastAPI backend
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to attach JWT Authorization Bearer token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('tg_auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to normalize error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = 'An unexpected error occurred while communicating with TransactionGuard API.';
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        message = error.response.data.detail.map((d) => d.msg || d).join(', ');
      } else {
        message = error.response.data.detail;
      }
    } else if (
      error.response?.status === 500 &&
      typeof error.response?.data === 'string' &&
      (error.response.data.includes('ECONNREFUSED') || error.response.data.includes('Proxy error'))
    ) {
      message = 'Backend server is offline or unreachable on port 8000. Please start the backend server.';
    } else if (error.response?.status === 502 || error.response?.status === 503 || error.code === 'ECONNREFUSED') {
      message = 'Backend server is offline or unreachable on port 8000. Please start the backend server.';
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

export default api;
