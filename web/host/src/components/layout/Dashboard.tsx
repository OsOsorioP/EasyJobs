import React, { Suspense, useState } from 'react';
import { useAuthStore } from '../../hooks/useAuthStore';
import { LogOut, HelpCircle, Loader2, UploadCloud, Cpu, RefreshCw, AlertCircle } from 'lucide-react';
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';

interface RemoteErrorBoundaryProps {
  children: React.ReactNode;
  fallback: React.ReactNode;
}

class RemoteErrorBoundary extends React.Component<RemoteErrorBoundaryProps, { hasError: boolean }> {
  constructor(props: RemoteErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error("Fallo al inicializar módulo remoto de análisis:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

const RemoteSearchContainer = React.lazy(() => import('intelligence/SearchContainer'));

export default function DashboardLayout() {
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const [retryKey, setRetryKey] = useState(0);

  const isCognitiveActive = location.pathname.includes('/dashboard/cognitive');
  const isEtlActive = location.pathname.includes('/dashboard/etl');

  const handleRetry = () => {
    setRetryKey(prev => prev + 1);
    window.location.reload();
  };

  const remoteFallback = (mode: 'search' | 'etl') => (
    <div className="p-8 border border-slate-200 bg-white rounded-2xl shadow-xs text-center max-w-xl mx-auto my-12 animate-fade-in">
      <div className="w-12 h-12 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-4">
        <AlertCircle className="w-6 h-6 text-amber-600" />
      </div>
      <h3 className="font-bold text-slate-900 text-lg">Módulo temporalmente fuera de línea</h3>
      <p className="text-sm text-slate-500 mt-2 leading-relaxed">
        No hemos podido cargar la interfaz de {mode === 'search' ? 'búsqueda y análisis' : 'carga de archivos'}.
        Esto puede deberse a una actualización del sistema. Por favor, intente recargar el módulo.
      </p>
      <button
        onClick={handleRetry}
        className="mt-6 inline-flex items-center gap-2 bg-slate-900 text-white hover:bg-slate-800 text-xs font-bold py-2.5 px-5 rounded-xl cursor-pointer transition-all shadow-xs"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        <span>Reintentar conexión</span>
      </button>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="sticky top-0 h-screen w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 shadow-lg">
        <div className="h-16 flex items-center px-6 border-b border-slate-800/60">
          <span className="text-xl font-bold text-white tracking-wider">EasyJobs</span>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          <Link
            to="/dashboard/etl"
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
              isEtlActive ? 'bg-indigo-600 text-white shadow-sm' : 'hover:bg-slate-800/60 hover:text-white'
            }`}
          >
            <UploadCloud className="w-5 h-5" />
            <span>Carga de Candidatos</span>
          </Link>

          <Link
            to="/dashboard/cognitive"
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
              isCognitiveActive ? 'bg-indigo-600 text-white shadow-sm' : 'hover:bg-slate-800/60 hover:text-white'
            }`}
          >
            <Cpu className="w-5 h-5" />
            <span>Consola de Análisis</span>
          </Link>
        </nav>

        <div className="p-4 border-t border-slate-800/60 bg-slate-950/20 space-y-3">
          <div className="px-2">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Sesión iniciada</p>
            <p className="text-sm font-bold text-white truncate mt-1">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-semibold text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer"
          >
            <LogOut className="w-5 h-5" />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-10 h-16 bg-white/95 backdrop-blur border-b border-slate-200/80 flex items-center justify-between px-8 shadow-xs">
          <h2 className="text-lg font-bold text-slate-800">
            {isCognitiveActive ? 'Consola de Análisis Inteligente' : 'Portal de Carga Masiva'}
          </h2>
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <HelpCircle className="w-5 h-5" />
            <span>Ayuda</span>
          </div>
        </header>

        <div className="flex-1 p-8 overflow-y-auto">
          <Routes>
            <Route 
              path="cognitive" 
              element={
                <RemoteErrorBoundary fallback={remoteFallback('search')}>
                  <Suspense
                    fallback={
                      <div className="p-12 flex flex-col items-center justify-center bg-white rounded-2xl border border-slate-200/60 shadow-xs">
                        <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mb-3" />
                        <p className="text-sm text-slate-600 font-semibold">Cargando consola de análisis...</p>
                      </div>
                    }
                  >
                    <RemoteSearchContainer key={retryKey} mode="search" />
                  </Suspense>
                </RemoteErrorBoundary>
              } 
            />
            <Route 
              path="etl" 
              element={
                <RemoteErrorBoundary fallback={remoteFallback('etl')}>
                  <Suspense
                    fallback={
                      <div className="p-12 flex flex-col items-center justify-center bg-white rounded-2xl border border-slate-200/60 shadow-xs">
                        <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mb-3" />
                        <p className="text-sm text-slate-600 font-semibold">Cargando portal de carga masiva...</p>
                      </div>
                    }
                  >
                    <RemoteSearchContainer key={retryKey} mode="etl" />
                  </Suspense>
                </RemoteErrorBoundary>
              } 
            />
            <Route path="*" element={<Navigate to="cognitive" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}