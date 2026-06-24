import { create } from 'zustand';
import { decodeToken, type DecodedToken } from '../lib/utils/jwt';

export type UserRole = 'admin' | 'recruiter' | 'candidate';

interface UserInfo {
  id: string;
  email: string;
  role: UserRole;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserInfo | null;
  isAuthenticated: boolean;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUserFromToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => {
  const storedAccess = localStorage.getItem('access_token');
  const storedRefresh = localStorage.getItem('refresh_token');
  let initialUser: UserInfo | null = null;

  if (storedAccess) {
    const decoded: DecodedToken | null = decodeToken(storedAccess);
    if (decoded && decoded.exp * 1000 > Date.now()) {
      initialUser = {
        id: decoded.sub,
        email: decoded.email || 'usuario@easyjobs.com',
        role: decoded.role,
      };
    }
  }

  return {
    accessToken: storedAccess,
    refreshToken: storedRefresh,
    user: initialUser,
    isAuthenticated: !!initialUser,

    setTokens: (accessToken: string, refreshToken: string) => {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      
      const decoded = decodeToken(accessToken);
      const userObj: UserInfo | null = decoded ? {
        id: decoded.sub,
        email: decoded.email || 'usuario@easyjobs.com',
        role: decoded.role
      } : null;

      set({
        accessToken,
        refreshToken,
        user: userObj,
        isAuthenticated: !!userObj,
      });
    },

    setUserFromToken: (token: string) => {
      const decoded = decodeToken(token);
      if (decoded) {
        set({
          user: {
            id: decoded.sub,
            email: decoded.email || 'usuario@easyjobs.com',
            role: decoded.role,
          },
          isAuthenticated: true,
        });
      }
    },

    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({
        accessToken: null,
        refreshToken: null,
        user: null,
        isAuthenticated: false,
      });
    },
  };
});