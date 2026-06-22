export interface DecodedToken {
  sub: string;
  email?: string;
  role: 'admin' | 'recruiter' | 'candidate';
  type: 'access' | 'refresh';
  exp: number;
  iat: number;
}

/**
 * Decodifica de forma segura un token JWT en formato string.
 * Retorna el payload tipado o null si el token es inválido o tiene un formato incorrecto.
 */
export function decodeToken(token: string): DecodedToken | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }
    
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    
    return JSON.parse(jsonPayload) as DecodedToken;
  } catch (error) {
    console.error("Error al decodificar el token JWT:", error);
    return null;
  }
}

/**
 * Determina si un token JWT ha expirado.
 */
export function isTokenExpired(token: string): boolean {
  const decoded = decodeToken(token);
  if (!decoded) return true;
  return decoded.exp * 1000 < Date.now() + 10000;
}