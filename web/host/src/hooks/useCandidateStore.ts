import { create } from 'zustand';
import { candidateService } from '../lib/services/candidate.service';
import type { Candidate, CandidateFormData } from '../types';

interface CandidateState {
  candidates: Candidate[];
  isLoading: boolean;
  error: string | null;
  fetchCandidates: () => Promise<void>;
  createCandidate: (candidateData: CandidateFormData) => Promise<boolean>;
  updateCandidate: (id: string, candidateData: Partial<CandidateFormData>) => Promise<boolean>;
  deleteCandidate: (id: string) => Promise<boolean>;
}

export const useCandidateStore = create<CandidateState>((set, get) => ({
  candidates: [],
  isLoading: false,
  error: null,

  fetchCandidates: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await candidateService.getAll();
      set({ candidates: data, isLoading: false });
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || "No se pudo conectar con el microservicio de candidatos.",
        isLoading: false 
      });
    }
  },

  createCandidate: async (candidateData) => {
    set({ isLoading: true, error: null });
    try {
      await candidateService.create(candidateData);
      await get().fetchCandidates();
      return true;
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || "Error al persistir el candidato.", 
        isLoading: false 
      });
      return false;
    }
  },

  updateCandidate: async (id, candidateData) => {
    set({ isLoading: true, error: null });
    try {
      await candidateService.update(id, candidateData);
      await get().fetchCandidates();
      return true;
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || "Error al actualizar la ficha del candidato.", 
        isLoading: false 
      });
      return false;
    }
  },

  deleteCandidate: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await candidateService.delete(id);
      await get().fetchCandidates();
      return true;
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || "Error al eliminar el candidato. Verifique sus permisos de administrador.", 
        isLoading: false 
      });
      return false;
    }
  }
}));