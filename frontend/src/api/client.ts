import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config.__isRetryRequest) {
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          const refreshResponse = await api.post('/auth/refresh', {
            access_token: localStorage.getItem('accessToken'),
            refresh_token: refreshToken,
            token_type: 'bearer'
          })
          localStorage.setItem('accessToken', refreshResponse.data.access_token)
          localStorage.setItem('refreshToken', refreshResponse.data.refresh_token)
          error.config.__isRetryRequest = true
          return api(error.config)
        } catch (refreshError) {
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
