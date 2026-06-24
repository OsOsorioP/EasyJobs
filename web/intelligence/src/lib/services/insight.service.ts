import { api } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { type InsightResult, InsightResultSchema } from '../../types';

export const insightService = {
  async generate(query: string): Promise<InsightResult> {
    const { data } = await api.post(ENDPOINTS.INSIGHTS, {
      query,
    });

    return InsightResultSchema.parse(data);
  }
};