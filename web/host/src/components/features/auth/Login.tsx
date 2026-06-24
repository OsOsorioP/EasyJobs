import React, { useState } from 'react';
import { useAuthStore } from '../../../hooks/useAuthStore';
import { api } from '../../../lib/api/client';
import { Lock, Mail, AlertCircle, UserPlus, Loader2 } from 'lucide-react';
import { ENDPOINTS } from '../../../lib/api/endpoints';

interface LoginProps {
  onNavigateToRegister: () => void;
}

export default function Login({ onNavigateToRegister }: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const setTokens = useAuthStore((state) => state.setTokens);

  const handleRealLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await api.post(ENDPOINTS.LOGIN, {
        email,
        password,
      });
      const { access_token, refresh_token } = response.data;
      setTokens(access_token, refresh_token);
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError('El correo o la contraseña introducidos no son correctos. Por favor, inténtelo de nuevo.');
      } else {
        setError('No ha sido posible conectar con la plataforma. Por favor, compruebe su conexión o inténtelo más tarde.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">EasyJobs</h1>
          <p className="text-sm text-slate-500 mt-2">Plataforma inteligente de gestión y selección de talento</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-100 text-rose-700 text-sm flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-500 mt-0.5" />
            <span className="leading-relaxed">{error}</span>
          </div>
        )}

        <form onSubmit={handleRealLogin} className="space-y-5">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Correo electrónico
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 h-5 w-5 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl text-sm transition-all placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white"
                placeholder="nombre@empresa.com"
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Contraseña
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-5 w-5 text-slate-400" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl text-sm transition-all placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white"
                placeholder="••••••••"
                disabled={isLoading}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-slate-900 text-white py-3 px-4 rounded-xl text-sm font-semibold hover:bg-slate-800 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 cursor-pointer mt-2 shadow-xs"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Iniciando sesión...</span>
              </>
            ) : (
              <span>Ingresar</span>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-100 text-center">
          <button
            onClick={onNavigateToRegister}
            disabled={isLoading}
            className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-slate-950 transition-colors cursor-pointer disabled:opacity-50"
          >
            <UserPlus className="w-4 h-4" />
            ¿No tiene una cuenta activa? Regístrese aquí
          </button>
        </div>
      </div>
    </div>
  );
}