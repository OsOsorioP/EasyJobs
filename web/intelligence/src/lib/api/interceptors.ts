import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

export function setupInterceptors(axiosInstance: AxiosInstance): void {
  axiosInstance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  axiosInstance.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error) => {
      if (error.response?.status === 401) {
        console.warn('Sesión expirada o token no válido en el microfrontend de inteligencia');
      }
      return Promise.reject(error);
    }
  );
}