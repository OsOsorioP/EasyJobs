from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class ExtractedCandidate(BaseModel):
    """Modelo estructurado que el LLM debe obligatoriamente completar a partir del texto del CV."""
    name: str = Field(description="Nombre completo del candidato encontrado en la hoja de vida.")
    email: EmailStr = Field(description="Correo electrónico de contacto válido.")
    phone: Optional[str] = Field(None, description="Número de teléfono de contacto.")
    summary: Optional[str] = Field(None, description="Un resumen profesional objetivo (máximo 3 líneas).")
    skills: Optional[str] = Field(None, description="Lista de habilidades técnicas clave separadas por comas.")
    experience: Optional[str] = Field(None, description="Breve recuento de su experiencia o cargos anteriores.")