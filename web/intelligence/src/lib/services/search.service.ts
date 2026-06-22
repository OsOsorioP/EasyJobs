import { api } from '../api/client';
import { ENDPOINTS } from '../api/endpoints';

export interface SearchCandidateResult {
  id: string;
  score: number;
  name: string;
  email: string;
  skills: string;
  experience: string;
  summary: string;
}

export const searchService = {
  async search(query: string, limit: number = 5): Promise<SearchCandidateResult[]> {
    const response = await api.post<SearchCandidateResult[]>(ENDPOINTS.SEARCH, {
      query,
      limit,
    });
    return response.data;
  }
};
