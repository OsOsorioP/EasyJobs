import axios from "axios";
import { setupInterceptors } from './interceptors';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

setupInterceptors(api);