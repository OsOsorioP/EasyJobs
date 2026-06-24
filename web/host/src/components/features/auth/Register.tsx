import React, { useState } from 'react';
import { authService } from '../../../lib/services/auth.service';
import { Lock, Mail, AlertCircle, ArrowLeft, CheckCircle, Loader2 } from 'lucide-react';

interface RegisterProps {
  onBackToLogin: () => void;
}

export default function Register({ onBackToLogin }: RegisterProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password.length < 8) {
      setError('La contraseña debe tener una longitud mínima de 8 caracteres.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Las contraseñas introducidas no coinciden.');
      return;
    }

    setIsLoading(true);

    try {
      await authService.register({ email, password });
      setIsSuccess(true);
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('Este correo electrónico ya se encuentra registrado en el sistema.');
      } else {
        setError('No ha sido posible procesar el registro en este momento. Por favor, inténtelo de nuevo más tarde.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-100 p-8 text-center animate-fade-in">
          <div className="mx-auto w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
            <CheckCircle className="w-10 h-10 text-emerald-500" />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">¡Registro completado!</h2>
          <p className="text-sm text-slate-500 mt-3 leading-relaxed">
            Su cuenta ha sido creada de manera satisfactoria. Ya puede acceder a todas las funciones utilizando sus nuevas credenciales.
          </p>
          <button
            onClick={onBackToLogin}
            className="mt-8 w-full bg-slate-900 text-white py-3 px-4 rounded-xl text-sm font-semibold hover:bg-slate-800 transition-all cursor-pointer shadow-xs"
          >
            Ir al inicio de sesión
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
        <button
          onClick={onBackToLogin}
          disabled={isLoading}
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors mb-8 cursor-pointer disabled:opacity-50"
        >
          <ArrowLeft className="w-4 h-4" />
          Volver a iniciar sesión
        </button>

        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">EasyJobs</h1>
          <p className="text-sm text-slate-500 mt-2">Cree su cuenta de acceso profesional</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-100 text-rose-700 text-sm flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-500 mt-0.5" />
            <span className="leading-relaxed">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4.5">
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
                placeholder="ejemplo@empresa.com"
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
                placeholder="Mínimo 8 caracteres"
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Confirmar contraseña
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-5 w-5 text-slate-400" />
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl text-sm transition-all placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white"
                placeholder="Repita su contraseña"
                disabled={isLoading}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-slate-900 text-white py-3 px-4 rounded-xl text-sm font-semibold hover:bg-slate-800 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 cursor-pointer mt-4 shadow-xs"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Procesando registro...</span>
              </>
            ) : (
              <span>Registrarse</span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}