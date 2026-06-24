import React, { useState } from 'react';
import {
  Search, Cpu, CheckCircle2, AlertTriangle, Briefcase, Sparkles,
  UploadCloud, FileSpreadsheet, Archive, Check, AlertCircle, RefreshCw, Loader2,
  User, Star, Trophy,
} from 'lucide-react';
import { etlService } from './lib/services/etl.service';
import { insightService } from './lib/services/insight.service';
import { searchService, type SearchCandidateResult } from './lib/services/search.service';
import { isComparisonInsight, type InsightResult } from './types';

interface SearchContainerProps {
  mode?: 'search' | 'etl';
}

export default function SearchContainer({ mode }: SearchContainerProps) {
  const [activeTab, setActiveTab] = useState<'search' | 'etl'>('search');
  const currentTab = mode || activeTab;

  const [semanticQuery, setSemanticQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchCandidateResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  const [query, setQuery] = useState('');
  const [insight, setInsight] = useState<InsightResult | null>(null);
  const [isLoadingInsight, setIsLoadingInsight] = useState(false);
  const [insightError, setInsightError] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState<SearchCandidateResult | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [etlType, setEtlType] = useState<'csv' | 'zip'>('csv');
  const [isUploading, setIsUploading] = useState(false);
  const [etlResult, setEtlResult] = useState<{ status: string; total_records?: number; total_pdfs_processed?: number } | null>(null);
  const [etlError, setEtlError] = useState('');

  const handleSemanticSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!semanticQuery.trim()) return;

    setIsSearching(true);
    setSearchError('');
    setSearchResults([]);
    setInsight(null);
    setSelectedCandidate(null);

    try {
      const data = await searchService.search(semanticQuery);
      setSearchResults(data);
    } catch (err: any) {
      setSearchError("No ha sido posible completar la búsqueda en este momento. Por favor, compruebe los datos de su consulta.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleAnalyzeCandidate = async (candidate: SearchCandidateResult) => {
    setSelectedCandidate(candidate);
    setIsLoadingInsight(true);
    setInsightError('');
    setInsight(null);

    const jobContext = semanticQuery.trim()
      ? `La búsqueda que originó este candidato fue: "${semanticQuery}". Usa esa descripción como referencia de vacante para calcular el score de compatibilidad técnica.`
      : 'Evalúa al candidato de forma genérica y asigna un score estimado según su nivel de senioridad y completitud del perfil.';

    try {
      const data = await insightService.generate(
        `Realiza una evaluación técnica detallada del candidato ${candidate.name} con ID ${candidate.id}. ${jobContext}`
      );
      setInsight(data);
    } catch (err: any) {
      console.error('Error al generar insights del candidato:', err);
      setInsightError(
        err.response?.data?.detail ||
        'El servicio cognitivo de IA falló al procesar el reporte de este candidato.'
      );
    } finally {
      setIsLoadingInsight(false);
    }
  };

  const handleGenerateInsight = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoadingInsight(true);
    setInsightError('');
    setInsight(null);
    setSelectedCandidate(null);

    try {
      const data = await insightService.generate(query);
      setInsight(data);
    } catch (err: any) {
      console.error('Error al generar la consulta del asistente:', err);
      setInsightError(
        err.response?.data?.detail ||
        "El asistente de consultas no se encuentra disponible. Por favor, inténtelo de nuevo más tarde."
      );
    } finally {
      setIsLoadingInsight(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setEtlError('');
      setEtlResult(null);

      if (file.name.endsWith('.csv')) {
        setEtlType('csv');
      } else if (file.name.endsWith('.zip')) {
        setEtlType('zip');
      }
    }
  };

  const handleUploadETL = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setEtlError('');
    setEtlResult(null);

    try {
      const response = await etlService.uploadEtl(selectedFile, etlType);
      setEtlResult(response);
    } catch (err: any) {
      setEtlError("Ocurrió un problema durante el procesamiento del archivo masivo. Verifique que cumpla con el formato indicado.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 w-full">
      {!mode && (
        <div className="flex border-b border-slate-200 bg-white p-2 rounded-2xl shadow-xs">
          <button
            onClick={() => setActiveTab('search')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all cursor-pointer ${currentTab === 'search'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:bg-slate-50'
              }`}
          >
            <Cpu className="w-4 h-4" />
            <span>Consola de Análisis</span>
          </button>
          <button
            onClick={() => setActiveTab('etl')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all cursor-pointer ${currentTab === 'etl'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:bg-slate-50'
              }`}
          >
            <UploadCloud className="w-4 h-4" />
            <span>Carga Masiva</span>
          </button>
        </div>
      )}

      {currentTab === 'search' && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            <div className="lg:col-span-2 bg-white rounded-2xl shadow-xs border border-slate-200/70 p-6 flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
                  <Search className="w-5 h-5 text-indigo-600" />
                  Búsqueda Inteligente de Candidatos
                </h3>
                <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                  Realice consultas en lenguaje natural para encontrar candidatos en base a requerimientos de perfiles, experiencia o habilidades clave descritas en la vacante de manera inteligente.
                </p>

                {searchError && (
                  <div className="mb-4 p-4 rounded-xl bg-rose-50 border border-rose-100 text-rose-700 text-xs flex items-center gap-2.5">
                    <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                    <span>{searchError}</span>
                  </div>
                )}

                <form onSubmit={handleSemanticSearch} className="flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
                    <input
                      type="text"
                      required
                      value={semanticQuery}
                      onChange={(e) => setSemanticQuery(e.target.value)}
                      placeholder="Ej: Busco perfiles con alta trayectoria en el desarrollo de microservicios con Python..."
                      className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isSearching}
                    className="bg-indigo-600 text-white font-semibold text-sm px-6 py-3 rounded-xl flex items-center gap-2 hover:bg-indigo-700 transition-colors disabled:bg-indigo-400 cursor-pointer shadow-xs shrink-0"
                  >
                    {isSearching ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <span>Buscar</span>
                    )}
                  </button>
                </form>
              </div>

              <div className="mt-8 space-y-3.5 flex-1 overflow-y-auto max-h-[360px] pr-1">
                {isSearching ? (
                  <div className="space-y-3">
                    {[1, 2].map((i) => (
                      <div key={i} className="p-5 rounded-xl border border-slate-100 bg-white space-y-3 animate-pulse">
                        <div className="flex justify-between items-center">
                          <div className="h-4 bg-slate-200 rounded-md w-1/3"></div>
                          <div className="h-4 bg-slate-200 rounded-md w-1/6"></div>
                        </div>
                        <div className="h-3 bg-slate-100 rounded-md w-1/4"></div>
                        <div className="h-3 bg-slate-100 rounded-md w-1/2"></div>
                      </div>
                    ))}
                  </div>
                ) : searchResults.length === 0 ? (
                  <div className="text-center py-12 border border-dashed border-slate-200 rounded-xl bg-slate-50/40">
                    <p className="text-xs text-slate-400">Introduzca su criterio de búsqueda técnica en el campo superior para analizar candidatos compatibles.</p>
                  </div>
                ) : (
                  searchResults.map((candidate) => (
                    <div
                      key={candidate.id}
                      className={`p-4 rounded-xl border transition-all flex flex-col md:flex-row justify-between items-start md:items-center gap-4 ${selectedCandidate?.id === candidate.id
                          ? 'border-indigo-500 bg-indigo-50/20 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 bg-white hover:shadow-xs'
                        }`}
                    >
                      <div className="space-y-1.5 flex-1 min-w-0">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <User className="w-4 h-4 text-slate-400 shrink-0" />
                          <h4 className="font-bold text-sm text-slate-900 truncate">{candidate.name}</h4>
                          <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full">
                            {(candidate.score * 100).toFixed(0)}% Compatibilidad
                          </span>
                        </div>
                        <p className="text-xs text-slate-500">{candidate.email}</p>
                        {candidate.skills && (
                          <div className="flex items-center gap-1.5 mt-1 text-[11px] text-slate-600">
                            <Star className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                            <span className="truncate max-w-[320px]"><strong>Habilidades:</strong> {candidate.skills}</span>
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleAnalyzeCandidate(candidate)}
                        disabled={isLoadingInsight && selectedCandidate?.id === candidate.id}
                        className="bg-slate-900 text-white font-semibold text-xs py-2 px-4 rounded-lg flex items-center gap-1.5 hover:bg-slate-800 transition-colors disabled:bg-slate-400 cursor-pointer shadow-xs shrink-0 self-end md:self-auto"
                      >
                        {isLoadingInsight && selectedCandidate?.id === candidate.id ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span>Analizando...</span>
                          </>
                        ) : (
                          <>
                            <Cpu className="w-3.5 h-3.5" />
                            <span>Analizar perfil</span>
                          </>
                        )}
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-xs border border-slate-200/70 p-6 flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  Asistente de Consultas y Comparativas
                </h3>
                <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                  Realice consultas avanzadas para contrastar perfiles, solicitar resúmenes directos o estructurar candidatos según necesidades específicas.
                </p>

                {insightError && (
                  <div className="mb-4 p-4 rounded-xl bg-rose-50 border border-rose-100 text-rose-700 text-xs flex items-center gap-2.5">
                    <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                    <span>{insightError}</span>
                  </div>
                )}

                <form onSubmit={handleGenerateInsight} className="space-y-4">
                  <textarea
                    required
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ej: Compara los 3 mejores candidatos con experiencia en desarrollo mobile y dime cuál es más apto para un rol de Tech Lead Mobile..."
                    className="w-full h-36 p-4 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-slate-950 focus:border-transparent resize-none leading-relaxed"
                  />
                  <button
                    type="submit"
                    disabled={isLoadingInsight}
                    className="w-full bg-slate-900 text-white font-semibold text-xs py-3 rounded-xl flex items-center justify-center gap-2 hover:bg-slate-800 transition-colors disabled:bg-slate-400 cursor-pointer shadow-xs"
                  >
                    {isLoadingInsight && !selectedCandidate ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Analizando requerimientos...</span>
                      </>
                    ) : (
                      <>
                        <Cpu className="w-3.5 h-3.5" />
                        <span>Ejecutar consulta</span>
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

          </div>

          {isLoadingInsight && (
            <div className="p-12 flex flex-col items-center justify-center bg-white rounded-2xl border border-slate-200/70 shadow-xs animate-fade-in">
              <Loader2 className="w-10 h-10 animate-spin text-indigo-600 mb-4" />
              <p className="text-sm text-slate-700 font-bold">
                {selectedCandidate ? `Generando evaluación para ${selectedCandidate.name}...` : 'Procesando consulta y estructurando información...'}
              </p>
              <p className="text-xs text-slate-400 mt-1.5">Esto puede tomar un momento mientras consolidamos el perfil.</p>
            </div>
          )}

          {insight && !isComparisonInsight(insight) && (
            <div className="bg-white rounded-2xl shadow-xs border border-slate-200/70 overflow-hidden animate-fade-in">
              <div className="bg-slate-900 p-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-indigo-500/20 p-2.5 rounded-xl">
                    <Cpu className="w-5 h-5 text-indigo-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-bold text-sm">
                      Informe detallado de perfil: {insight.candidate_name || selectedCandidate?.name || 'Candidato'}
                    </h4>
                    <p className="text-[10px] text-slate-400 tracking-wider uppercase font-bold mt-0.5">Informe consolidado en tiempo real</p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 border-b border-slate-100 pb-6">
                  <div className="md:col-span-2 flex items-start gap-4">
                    <div className="bg-slate-100 p-3 rounded-xl text-slate-800">
                      <Briefcase className="w-6 h-6 text-slate-700" />
                    </div>
                    <div>
                      <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Cargo sugerido</span>
                      <h5 className="text-xl font-bold text-slate-900 mt-1">{insight.suggested_role || 'Generalista técnico'}</h5>
                    </div>
                  </div>

                  <div className="flex flex-col md:items-end justify-center">
                    <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Ajuste de vacante</span>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-3xl font-black text-indigo-600">
                        {(insight.score * 100).toFixed(0)}%
                      </span>
                      <span className="text-xs text-slate-400">compatibilidad</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-slate-50 rounded-xl p-3">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Hard Skills</span>
                    <p className="text-lg font-bold text-slate-900">{(insight.hard_skills_score * 100).toFixed(0)}%</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-3">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Experiencia</span>
                    <p className="text-lg font-bold text-slate-900">{(insight.experience_score * 100).toFixed(0)}%</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-3">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Metodología</span>
                    <p className="text-lg font-bold text-slate-900">{(insight.methodology_score * 100).toFixed(0)}%</p>
                  </div>
                </div>

                <div className="space-y-2.5">
                  <h5 className="text-xs font-bold text-slate-700 uppercase tracking-widest">Resumen Ejecutivo</h5>
                  <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 border border-slate-100 p-4.5 rounded-xl text-justify">
                    {insight.summary}
                  </p>
                </div>

                {((insight.strengths && insight.strengths.length > 0) || (insight.weaknesses && insight.weaknesses.length > 0)) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                    <div className="space-y-4">
                      <h5 className="text-xs font-bold text-slate-800 uppercase tracking-widest flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                        Fortalezas del candidato
                      </h5>
                      <ul className="space-y-3">
                        {insight.strengths?.map((strength, index) => (
                          <li key={index} className="text-sm text-slate-600 flex items-start gap-2.5 leading-relaxed">
                            <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5 bg-emerald-50 rounded" />
                            <span>{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="space-y-4">
                      <h5 className="text-xs font-bold text-slate-800 uppercase tracking-widest flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-amber-500" />
                        Brechas o puntos a evaluar
                      </h5>
                      <ul className="space-y-3">
                        {insight.weaknesses?.map((weakness, index) => (
                          <li key={index} className="text-sm text-slate-600 flex items-start gap-2.5 leading-relaxed">
                            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5 bg-amber-50 rounded" />
                            <span>{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {insight && isComparisonInsight(insight) && (
            <div className="bg-white rounded-2xl shadow-xs border border-slate-200/70 overflow-hidden animate-fade-in">
              <div className="bg-slate-900 p-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-amber-500/20 p-2.5 rounded-xl">
                    <Sparkles className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-bold text-sm">Comparativa de candidatos</h4>
                    <p className="text-[10px] text-slate-400 tracking-wider uppercase font-bold mt-0.5">
                      Evaluados contra: {insight.evaluated_against}
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-6">
                {insight.winner_name && (
                  <div className="flex items-start gap-4 bg-amber-50 border border-amber-100 rounded-xl p-4.5">
                    <div className="bg-amber-100 p-2.5 rounded-xl shrink-0">
                      <Trophy className="w-5 h-5 text-amber-600" />
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs text-amber-700 font-bold uppercase tracking-wider">Candidato más apto</span>
                      <h5 className="text-lg font-bold text-slate-900">{insight.winner_name}</h5>
                      <p className="text-sm text-slate-600 leading-relaxed">{insight.verdict}</p>
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {insight.candidates.map((c) => (
                    <div
                      key={c.candidate_id ?? c.candidate_name}
                      className={`p-4.5 rounded-xl border space-y-3 ${
                        c.candidate_id === insight.winner_candidate_id
                          ? 'border-amber-300 bg-amber-50/30'
                          : 'border-slate-200 bg-white'
                      }`}
                    >
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-slate-400" />
                          <h6 className="font-bold text-sm text-slate-900">{c.candidate_name}</h6>
                          {c.candidate_id === insight.winner_candidate_id && (
                            <span className="text-[10px] font-bold bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">Más apto</span>
                          )}
                        </div>
                        <span className="text-sm font-black text-indigo-600">{(c.score * 100).toFixed(0)}% compatibilidad</span>
                      </div>

                      <div className="grid grid-cols-3 gap-3 text-center">
                        <div className="bg-slate-50 rounded-lg py-2">
                          <span className="text-[9px] text-slate-500 font-bold uppercase">Hard Skills</span>
                          <p className="text-sm font-bold text-slate-800">{(c.hard_skills_score * 100).toFixed(0)}%</p>
                        </div>
                        <div className="bg-slate-50 rounded-lg py-2">
                          <span className="text-[9px] text-slate-500 font-bold uppercase">Experiencia</span>
                          <p className="text-sm font-bold text-slate-800">{(c.experience_score * 100).toFixed(0)}%</p>
                        </div>
                        <div className="bg-slate-50 rounded-lg py-2">
                          <span className="text-[9px] text-slate-500 font-bold uppercase">Metodología</span>
                          <p className="text-sm font-bold text-slate-800">{(c.methodology_score * 100).toFixed(0)}%</p>
                        </div>
                      </div>

                      {c.summary && (
                        <p className="text-xs text-slate-600 leading-relaxed">{c.summary}</p>
                      )}

                      {(c.strengths.length > 0 || c.weaknesses.length > 0) && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                          {c.strengths.length > 0 && (
                            <ul className="space-y-1.5">
                              {c.strengths.map((s, i) => (
                                <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                                  <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                                  <span>{s}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                          {c.weaknesses.length > 0 && (
                            <ul className="space-y-1.5">
                              {c.weaknesses.map((w, i) => (
                                <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                                  <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                                  <span>{w}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {currentTab === 'etl' && (
        <div className="space-y-6 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-xs border border-slate-200/70 p-6">
            <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-indigo-600" />
              Procesamiento e Importación Masiva
            </h3>
            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
              Cargue perfiles de candidatos de forma masiva utilizando un archivo estructurado en formato (.csv) o mediante una carpeta comprimida (.zip) que contenga hojas de vida en formato (.pdf). El sistema extraerá de manera automática la información relevante para su posterior análisis.
            </p>

            {etlError && (
              <div className="mb-4 p-4 rounded-xl bg-rose-50 border border-rose-100 text-rose-700 text-xs flex items-center gap-2.5">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>{etlError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600">Seleccionar archivo</label>
                <div className="border-2 border-dashed border-slate-200 hover:border-indigo-300 rounded-2xl p-8 flex flex-col items-center justify-center bg-slate-50/50 transition-all relative group">
                  <input
                    type="file"
                    accept=".csv, .zip"
                    onChange={handleFileChange}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  {selectedFile ? (
                    <div className="text-center space-y-3">
                      {selectedFile.name.endsWith('.csv') ? (
                        <FileSpreadsheet className="w-12 h-12 text-emerald-500 mx-auto" />
                      ) : (
                        <Archive className="w-12 h-12 text-indigo-500 mx-auto" />
                      )}
                      <div>
                        <h5 className="text-sm font-bold text-slate-800">{selectedFile.name}</h5>
                        <p className="text-[10px] text-slate-400 mt-1">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center space-y-3">
                      <UploadCloud className="w-12 h-12 text-slate-400 group-hover:text-indigo-500 transition-colors mx-auto" />
                      <div>
                        <h5 className="text-sm font-bold text-slate-700">Arrastre aquí su archivo o pulse para buscar</h5>
                        <p className="text-[10px] text-slate-400 mt-1.5">Soporta formatos estructurados .csv y comprimidos .zip</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-col justify-between bg-slate-50/60 p-6 rounded-2xl border border-slate-100">
                <div className="space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">Especificaciones requeridas</h4>
                  <ul className="text-xs text-slate-500 space-y-3">
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full mt-1.5 shrink-0"></span>
                      <span><strong>Formatos estructurados:</strong> El archivo (.csv) debe contar obligatoriamente con las columnas de "Nombre" y "Email".</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full mt-1.5 shrink-0"></span>
                      <span><strong>Hojas de vida agrupadas:</strong> El archivo comprimido (.zip) debe contener exclusivamente documentos en formato (.pdf).</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full mt-1.5 shrink-0"></span>
                      <span><strong>Sincronización automatizada:</strong> Los perfiles quedarán listos para búsquedas inmediatamente después de procesarse.</span>
                    </li>
                  </ul>
                </div>

                <div className="pt-6">
                  <button
                    onClick={handleUploadETL}
                    disabled={!selectedFile || isUploading}
                    className="w-full bg-slate-900 text-white font-semibold text-sm py-3 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-slate-800 transition-colors disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed cursor-pointer shadow-xs"
                  >
                    {isUploading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Procesando registros de importación...</span>
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4" />
                        <span>Comenzar importación</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {etlResult && (
            <div className="bg-white rounded-2xl shadow-xs border border-emerald-100 p-6 flex items-start gap-4 animate-fade-in">
              <div className="bg-emerald-50 p-2.5 rounded-xl shrink-0">
                <Check className="w-6 h-6 text-emerald-600" />
              </div>
              <div className="space-y-1.5">
                <h4 className="text-sm font-bold text-emerald-900">¡Importación masiva completada con éxito!</h4>
                <p className="text-xs text-emerald-700 leading-relaxed">
                  Los registros de los candidatos han sido validados de forma segura e indexados dentro de la plataforma para su uso inmediato.
                </p>
                <div className="pt-2 flex items-center gap-4 text-xs font-semibold text-slate-600">
                  {etlResult.total_records !== undefined && (
                    <span>Candidatos registrados en el directorio: <strong className="text-slate-800">{etlResult.total_records}</strong></span>
                  )}
                  {etlResult.total_pdfs_processed !== undefined && (
                    <span>Documentos PDF analizados y digitalizados: <strong className="text-slate-800">{etlResult.total_pdfs_processed}</strong></span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}