from pathlib import Path
from functools import lru_cache

class PromptLoader:
    """Cargador defensivo de plantillas de prompts desde el almacenamiento de disco."""
    
    PROMPTS_BASE_PATH = Path(__file__).resolve().parent / "prompts"
    
    @classmethod
    @lru_cache(maxsize=10)
    def get_prompt(cls, category: str, version: str) -> str:
        file_path = cls.PROMPTS_BASE_PATH / category / f"{version}.txt"
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Fallo de inicialización de agente: No se localizó el prompt obligatorio en {file_path}"
            )
            
        return file_path.read_text(encoding="utf-8")