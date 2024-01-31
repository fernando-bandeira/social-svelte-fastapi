import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_PATH,
});

api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error?.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh');

      try {
        const refreshResponse = await api.post('/refresh/', {
          token: refreshToken,
        });

        localStorage.setItem('access', refreshResponse.data.access);
        localStorage.setItem('refresh', refreshResponse.data.refresh);

        return api(originalRequest);
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);
        throw refreshError;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
