import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../../hooks/useAuthStore';
import axios from 'axios';
import { ENDPOINTS } from './endpoints';

const API_BASE_URL = import.meta.env.VITE_API_URL;

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
        async (error) => {
            const originalRequest = error.config;

            if (error.response?.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;
                const refreshToken = localStorage.getItem('refresh_token');

                if (refreshToken) {
                    try {
                        const res = await axios.post(`${API_BASE_URL + ENDPOINTS.REFREST_TOKEN}`, {
                            refresh_token: refreshToken,
                        });

                        const { access_token, refresh_token } = res.data;

                        useAuthStore.getState().setTokens(access_token, refresh_token);

                        originalRequest.headers.Authorization = `Bearer ${access_token}`;
                        return originalRequest
                    } catch (refreshError) {
                        useAuthStore.getState().logout();
                        return Promise.reject(refreshError);
                    }
                }
            }
            return Promise.reject(error);
        }
    );
}