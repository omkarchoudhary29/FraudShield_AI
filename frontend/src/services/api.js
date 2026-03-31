import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/auth/logout');
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Transactions
export const getTransactions = async (params = {}) => {
  const response = await api.get('/transactions', { params });
  return response.data;
};

export const getTransaction = async (transactionId) => {
  const response = await api.get(`/transactions/${transactionId}`);
  return response.data;
};

export const ingestTransaction = async (transaction) => {
  const response = await api.post('/transactions/ingest', transaction);
  return response.data;
};

// Fraud
export const getFraudPrediction = async (transactionId) => {
  const response = await api.get(`/fraud/predictions/${transactionId}`);
  return response.data;
};

export const explainPrediction = async (transactionId) => {
  const response = await api.get(`/fraud/explain/${transactionId}`);
  return response.data;
};

export const getModelMetrics = async () => {
  const response = await api.get('/fraud/model-metrics');
  return response.data;
};

// Analytics
export const getOverviewMetrics = async (days = 7) => {
  const response = await api.get('/analytics/overview', { params: { days } });
  return response.data;
};

export const getFraudTrends = async (days = 30) => {
  const response = await api.get('/analytics/fraud-trends', { params: { days } });
  return response.data;
};

export const getTopMerchants = async (days = 30, limit = 10) => {
  const response = await api.get('/analytics/top-merchants', { params: { days, limit } });
  return response.data;
};

export const getDeviceRisk = async (days = 30) => {
  const response = await api.get('/analytics/device-risk', { params: { days } });
  return response.data;
};

export const getHourlyPatterns = async (days = 7) => {
  const response = await api.get('/analytics/hourly-patterns', { params: { days } });
  return response.data;
};

// Reviews
export const createReview = async (review) => {
  const response = await api.post('/reviews', review);
  return response.data;
};

export const getReviews = async (params = {}) => {
  const response = await api.get('/reviews', { params });
  return response.data;
};

export const getReviewQueue = async (limit = 50) => {
  const response = await api.get('/reviews/queue', { params: { limit } });
  return response.data;
};

// Alerts
export const getAlerts = async (params = {}) => {
  const response = await api.get('/alerts', { params });
  return response.data;
};

export const updateAlertStatus = async (alertId, status) => {
  const response = await api.patch(`/alerts/${alertId}/status`, null, {
    params: { status }
  });
  return response.data;
};

export default api;
