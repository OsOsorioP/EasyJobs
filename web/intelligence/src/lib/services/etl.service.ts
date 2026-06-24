import { api } from '../api/client';
import { ENDPOINTS } from '../api/endpoints';
import type { EtlResult, EtlType } from '../../types';

export const etlService = {
  async uploadEtl(file: File, type: EtlType): Promise<EtlResult> {
    const formData = new FormData();
    formData.append('file', file);

    const endpoint = type === 'csv' ? ENDPOINTS.ETL_CSV : ENDPOINTS.ETL_ZIP;

    const response = await api.post<EtlResult>(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};