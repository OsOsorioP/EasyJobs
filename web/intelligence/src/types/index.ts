import { z } from 'zod';

const scoreField = z
  .union([z.number(), z.string()])
  .transform((v) => {
    const n = typeof v === 'string' ? parseFloat(v) : v;
    return isNaN(n) ? 0 : Math.min(Math.max(n, 0), 1);
  })
  .default(0);

const stringArrayField = z
  .union([z.array(z.string()), z.null(), z.undefined()])
  .transform((v) => v ?? [])
  .default([]);

export const SingleInsightSchema = z.object({
  type: z.literal('single').default('single'),
  candidate_id: z.string().nullable().default(null),
  candidate_name: z.string().nullable().default(null),
  summary: z.string().default('Sin resumen disponible'),
  score: scoreField,
  hard_skills_score: scoreField,
  experience_score: scoreField,
  methodology_score: scoreField,
  strengths: stringArrayField,
  weaknesses: stringArrayField,
  suggested_role: z.string().default('N/A'),
});

export const ComparisonCandidateSchema = z.object({
  candidate_id: z.string().nullable().default(null),
  candidate_name: z.string().default('Candidato sin nombre'),
  score: scoreField,
  hard_skills_score: scoreField,
  experience_score: scoreField,
  methodology_score: scoreField,
  strengths: stringArrayField,
  weaknesses: stringArrayField,
  summary: z.string().default(''),
});

export const ComparisonInsightSchema = z.object({
  type: z.literal('comparison').default('comparison'),
  evaluated_against: z.string().default('No especificado'),
  candidates: z.array(ComparisonCandidateSchema).default([]),
  winner_candidate_id: z.string().nullable().default(null),
  winner_name: z.string().nullable().default(null),
  verdict: z.string().default('Sin veredicto disponible'),
});

export const InsightResultSchema = z.union([
  ComparisonInsightSchema,
  SingleInsightSchema,
]);

export type SingleInsightResult = z.infer<typeof SingleInsightSchema>;
export type ComparisonInsightResult = z.infer<typeof ComparisonInsightSchema>;
export type InsightResult = z.infer<typeof InsightResultSchema>;

export function isComparisonInsight(insight: InsightResult): insight is ComparisonInsightResult {
  return insight.type === 'comparison';
}

export type ActiveTab = 'search' | 'etl';
export type EtlType = 'csv' | 'zip';

export interface EtlResult {
  status: string;
  total_records?: number;
  total_pdfs_processed?: number;
}