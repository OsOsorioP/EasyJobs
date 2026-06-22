import { useState } from 'react';
import type { InsightResult } from '../types';
import { insightService } from '../lib/services/insight.service';

export function useInsight() {
  const [query, setQuery] = useState('');
  const [insight, setInsight] = useState<InsightResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSimulatedData, setIsSimulatedData] = useState(false);

  const handleGenerateInsight = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');
    setInsight(null);
    setIsSimulatedData(false);

    try {
      const data = await insightService.generate(query);
      setInsight(data);
    } catch (err) {
      console.warn("Fallo de conexión con el servicio real. Iniciando simulador.", err);
      setError("El servidor real de IA (puerto 8002) no respondió. Iniciando simulación local...");
      setIsSimulatedData(true);
    } finally {
        setIsLoading(false);
    }
  };

  return {
    query,
    setQuery,
    insight,
    isLoading,
    error,
    isSimulatedData,
    handleGenerateInsight,
  };
}