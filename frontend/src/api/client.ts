import axios from 'axios';

// Centralised Axios instance so every request shares base config and interceptors.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
});

api.interceptors.request.use((config) => {
  // Attach the bearer token when the user is authenticated.
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // When the API returns 401 we clear local session state so UI can react accordingly.
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
    return Promise.reject(error);
  }
);

export default api;
