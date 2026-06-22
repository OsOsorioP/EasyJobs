import SearchContainer from './SearchContainer';
import { Cpu } from 'lucide-react';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      <header className="bg-slate-900 border-b border-slate-800 text-white py-4 px-8 shadow-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-wider">Módulo de Inteligencia</h1>
              <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">
                Modo de Desarrollo Remoto (Puerto 5001)
              </p>
            </div>
          </div>
          <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs px-3 py-1 rounded-full font-bold">
            Federated Sandbox
          </span>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-8">
        <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-6 mb-8">
          <h2 className="text-lg font-bold text-slate-800 mb-2">Entorno de Simulación Integrado</h2>
          <p className="text-sm text-slate-500 leading-relaxed">
            Esta pantalla representa el contenedor del microfrontend expuesto mediante <strong>Module Federation</strong>.
            Utilícelo para construir y depurar la consola cognitiva antes de renderizarla dentro de la aplicación Host de producción.
          </p>
        </div>

        <SearchContainer />
      </main>

      <footer className="bg-slate-50 border-t border-slate-200 py-4 px-8 text-center text-xs text-slate-400">
        EasyJobs ATS Cognitive Module • 2026
      </footer>
    </div>
  );
}

export default App;