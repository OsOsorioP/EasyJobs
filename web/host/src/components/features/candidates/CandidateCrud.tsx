import { useEffect, useState } from 'react';
import { useCandidateStore } from '../../../hooks/useCandidateStore';
import { useAuthStore } from '../../../hooks/useAuthStore';
import { UserPlus, Search, AlertCircle, X } from 'lucide-react';
import CandidateRow from './CandidateRow';
import CandidateForm from './CandidateForm';
import type { Candidate, CandidateFormData } from '../../../types';

export default function CandidateCrud() {
  const { user } = useAuthStore();
  const { 
    candidates, isLoading, error,
    fetchCandidates, createCandidate, updateCandidate, deleteCandidate, deleteAllCandidates
  } = useCandidateStore();

  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCandidate, setEditingCandidate] = useState<Candidate | null>(null);
  const [isPurgeModalOpen, setIsPurgeModalOpen] = useState(false);

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  const canModify = user?.role === 'admin' || user?.role === 'recruiter';
  const canDelete = user?.role === 'admin' || user?.role === 'recruiter';

  const handleOpenCreateModal = () => {
    setEditingCandidate(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (candidate: Candidate) => {
    setEditingCandidate(candidate);
    setIsModalOpen(true);
  };

  const handleFormSubmit = async (payload: CandidateFormData) => {
    if (editingCandidate) {
      return await updateCandidate(editingCandidate.id, payload);
    } else {
      return await createCandidate(payload);
    }
  };

  const handleConfirmPurge = async () => {
    await deleteAllCandidates();
    setIsPurgeModalOpen(false);
  };

  const filteredCandidates = candidates.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.skills?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 w-full animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h3 className="text-xl font-bold text-slate-800">Directorio de Talento</h3>
          <p className="text-xs text-slate-500">Gestione y organice de manera centralizada los perfiles de los candidatos</p>
        </div>

        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
            Conexión segura
          </span>
          {canModify && (
            <button
              onClick={handleOpenCreateModal}
              className="bg-slate-900 text-white hover:bg-slate-800 font-semibold text-sm py-2 px-4 rounded-xl flex items-center gap-2 transition-all cursor-pointer shadow-xs hover:shadow-sm"
            >
              <UserPlus className="w-4 h-4" />
              <span>Agregar candidato</span>
            </button>
          )}
          {canDelete && candidates.length > 0 && (
            <button
              onClick={() => setIsPurgeModalOpen(true)}
              className="bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-100 font-semibold text-sm py-2 px-4 rounded-xl flex items-center gap-2 transition-all cursor-pointer"
            >
              <X className="w-4 h-4" />
              <span>Eliminar todos</span>
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-100 text-rose-700 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-rose-500" />
          <span className="leading-relaxed">{error}</span>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-xs border border-slate-200/60 p-4">
        <div className="relative">
          <Search className="absolute left-3.5 top-3.5 h-5 w-5 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar por nombre, habilidades o correo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all"
          />
        </div>
      </div>

      {isLoading && candidates.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/60 overflow-hidden">
          <div className="p-4 space-y-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="flex items-center justify-between py-3 border-b border-slate-100 last:border-0 animate-pulse">
                <div className="space-y-2.5 w-1/3">
                  <div className="h-4 bg-slate-200 rounded-md w-3/4"></div>
                  <div className="h-3 bg-slate-100 rounded-md w-1/2"></div>
                </div>
                <div className="h-4 bg-slate-100 rounded-md w-1/4"></div>
                <div className="h-4 bg-slate-100 rounded-md w-1/6"></div>
              </div>
            ))}
          </div>
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-200/60">
          <p className="text-slate-500 text-sm">No se encontraron candidatos con los criterios de búsqueda actuales.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-xs border border-slate-200/60 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-500 font-bold text-xs uppercase border-b border-slate-150">
                  <th className="py-4 px-6">Información Personal</th>
                  <th className="py-4 px-6">Habilidades clave</th>
                  <th className="py-4 px-6">Experiencia</th>
                  {canModify && <th className="py-4 px-6 text-right">Acciones</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {filteredCandidates.map((candidate) => (
                  <CandidateRow
                    key={candidate.id}
                    candidate={candidate}
                    canModify={canModify}
                    canDelete={canDelete}
                    onEdit={handleOpenEditModal}
                    onDelete={deleteCandidate}
                  />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-100 w-full max-w-lg overflow-hidden animate-zoom-in">
            <div className="bg-slate-900 p-5 flex items-center justify-between text-white">
              <h4 className="font-bold text-sm">
                {editingCandidate ? 'Modificar Información del Candidato' : 'Registrar Nuevo Candidato'}
              </h4>
              <button 
                onClick={() => setIsModalOpen(false)} 
                className="text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <CandidateForm
              editingCandidate={editingCandidate}
              onSubmit={handleFormSubmit}
              onCancel={() => setIsModalOpen(false)}
            />
          </div>
        </div>
      )}
      {isPurgeModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-100 w-full max-w-md overflow-hidden animate-zoom-in">
            <div className="p-6 space-y-4">
              <h4 className="font-bold text-base text-slate-900">¿Eliminar todos los candidatos?</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Esta acción eliminará permanentemente los {candidates.length} candidatos de tu directorio
                (Postgres y el índice vectorial). Úsalo antes de realizar una nueva carga ETL. No se puede deshacer.
              </p>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setIsPurgeModalOpen(false)}
                  className="text-slate-600 hover:bg-slate-50 font-semibold text-sm py-2 px-4 rounded-xl transition-all cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleConfirmPurge}
                  disabled={isLoading}
                  className="bg-rose-600 text-white hover:bg-rose-700 font-semibold text-sm py-2 px-4 rounded-xl transition-all cursor-pointer disabled:bg-rose-300"
                >
                  Sí, eliminar todo
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}