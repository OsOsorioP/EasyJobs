"""
Estrategia de Prompt Compression:
- Análisis de tokens: Contar tokens antes/después para optimizar.
- Generación de resúmenes previos: Usar LLM para resumir secciones largas.
- Eliminación de redundancias: Remover campos duplicados o irrelevantes.
- Preprocesamiento: Filtrar contexto a lo esencial antes de enviar al LLM.

Trade-offs:
- Pros: Reduce costo (menos tokens), menor latencia, evita límites de contexto.
- Cons: Posible pérdida de detalles sutiles, lo que podría afectar precisión en análisis complejos.
  Ej: En perfiles largos, un resumen podría omitir skills raras. Mitigación: Threshold configurable para compresión mínima.
"""

from typing import Dict, Any, List
import re

class ContextCompressor:
    """
    Preprocesa información del dominio Candidate
    para minimizar tokens enviados al LLM.
    """
    
    @staticmethod
    def compress(text: str) -> str:
        """Limpia el texto para reducir el consumo de tokens de Cohere/OpenAI/Groq."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s,.;-]', '', text)
        return text[:1500] if len(text) > 1500 else text

    @staticmethod
    def compress_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "profile": ContextCompressor._profile(candidate),
            "skills": ContextCompressor._skills(candidate.get("skills", [])),
            "experience": ContextCompressor._experience(candidate.get("experience", [])),
        }

    @staticmethod
    def to_prompt_context(candidate: Dict[str, Any]) -> str:
        """
        Salida final lista para inyectar en el prompt.
        """
        data = ContextCompressor.compress_candidate(candidate)

        blocks = []

        if data["profile"]:
            blocks.append(f"Perfil: {data['profile']}")

        if data["skills"]:
            blocks.append(f"Habilidades clave: {', '.join(data['skills'])}")

        if data["experience"]:
            blocks.append("Experiencia relevante:")
            for e in data["experience"]:
                blocks.append(
                    f"- {e['role']} ({e['years']} años): "
                    f"{'; '.join(e['highlights'])}"
                )

        return "\n".join(blocks)
    
    @staticmethod
    def preprocess_context(context: dict) -> dict:
        """Preprocesamiento para reducir contexto antes de LLM.

        Args:
            context (dict): Datos del candidato

        Returns:
            dict: Datos con contexto reduccido
        """
        if 'skills' in context and isinstance(context['skills'], list):
            context['skills'] = list(set(context['skills']))
        if 'summary' in context and len(context['summary']) > 1000:
            context['summary'] = context['summary'][:1000] + '...'
        return context

    @staticmethod
    def _profile(candidate: Dict[str, Any]) -> str | None:
        return candidate.get("summary")

    @staticmethod
    def _skills(skills: List[str]) -> List[str]:
        return sorted(set(skills))[:12]

    @staticmethod
    def _experience(experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        output = []

        for exp in experiences:
            output.append({
                "role": exp.get("role"),
                "years": exp.get("years"),
                "highlights": exp.get("achievements", [])[:3],
            })

        return output[:4]