import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  withCredentials: true,
});

// VULNERABILITY A05: Token in URL query string (improper placement of credentials)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token && config.url) {
    config.url = config.url + (config.url.includes('?') ? '&' : '?') + `token=${token}`;
  }
  return config;
});

export default api;

// Decoy: Proper use of Authorization header on a separate helper
export function apiWithAuthHeader(): typeof api {
  return axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    withCredentials: true,
  });
}