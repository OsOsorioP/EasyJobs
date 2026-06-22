import { z } from 'zod';

export const InsightResultSchema = z.object({
  summary: z.string().default('Sin resumen disponible'),
  score: z
    .union([z.number(), z.string()])
    .transform((v) => {
      const n = typeof v === 'string' ? parseFloat(v) : v;
      return isNaN(n) ? 0 : Math.min(Math.max(n, 0), 1);
    })
    .default(0),
  strengths: z
    .union([z.array(z.string()), z.null(), z.undefined()])
    .transform((v) => v ?? [])
    .default([]),
  weaknesses: z
    .union([z.array(z.string()), z.null(), z.undefined()])
    .transform((v) => v ?? [])
    .default([]),
  suggested_role: z.string().default('N/A'),
});

export type InsightResult = z.infer<typeof InsightResultSchema>;

export type ActiveTab = 'search' | 'etl';
export type EtlType = 'csv' | 'zip';

export interface EtlResult {
  status: string;
  total_records?: number;
  total_pdfs_processed?: number;
}