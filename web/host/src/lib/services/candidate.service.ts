import { api } from '../api/client';
import type { Candidate, CandidateFormData } from '../../types';

export const candidateService = {
  /**
   * Obtiene la lista de todos los candidatos desde el microservicio.
   */
  async getAll(): Promise<Candidate[]> {
    const response = await api.get<Candidate[]>('/candidates');
    return response.data;
  },

  /**
   * Registra un nuevo candidato en PostgreSQL.
   */
  async create(candidate: CandidateFormData): Promise<Candidate> {
    const response = await api.post<Candidate>('/candidates', candidate);
    return response.data;
  },

  /**
   * Modifica un perfil de candidato de manera persistente.
   */
  async update(id: string, candidate: Partial<CandidateFormData>): Promise<Candidate> {
    const response = await api.put<Candidate>(`/candidates/${id}`, candidate);
    return response.data;
  },

  /**
   * Elimina un candidato (requiere rol de administrador).
   */
  async delete(id: string): Promise<void> {
    await api.delete(`/candidates/${id}`);
  }
};