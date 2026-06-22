import { api } from '../api/client';
import type { TokenPair, UserLogin, UserRegister, UserRead } from '../../types';

export const authService = {
  /**
   * Registra un nuevo usuario en la base de datos a través de la API Gateway.
   */
  async register(data: UserRegister): Promise<UserRead> {
    const response = await api.post<UserRead>('/identity/api/v1/auth/register', data);
    return response.data;
  },

  /**
   * Inicia sesión de usuario y retorna la dupla de tokens de acceso y refresco.
   */
  async login(credentials: UserLogin): Promise<TokenPair> {
    const response = await api.post<TokenPair>('/identity/api/v1/auth/login', credentials);
    return response.data;
  },

  /**
   * Refresca el token de acceso utilizando un token de refresco válido.
   */
  async refresh(refreshToken: string): Promise<TokenPair> {
    const response = await api.post<TokenPair>('/identity/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  /**
   * Obtiene la información del perfil del usuario actualmente autenticado.
   */
  async getMe(): Promise<UserRead> {
    const response = await api.get<UserRead>('/identity/api/v1/auth/me');
    return response.data;
  }
};