import csv
import io
import re
import zipfile
from typing import List, Dict, Any
from pypdf import PdfReader

# Expresión regular estándar para validación básica de formato de correo electrónico
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class ETLParser:
    """Clase responsable de la lectura física, normalización y validación defensiva de archivos de entrada."""

    # Mapa de mapeo dinámico para homogeneizar cabeceras en español, inglés, mayúsculas y acentos
    HEADER_MAPPING = {
        "name": "name",
        "nombre": "name",
        "nombre completo": "name",
        "name complete": "name",
        "email": "email",
        "correo": "email",
        "correo electronico": "email",
        "correo electrónico": "email",
        "email address": "email",
        "phone": "phone",
        "telefono": "phone",
        "teléfono": "phone",
        "summary": "summary",
        "resumen": "summary",
        "skills": "skills",
        "habilidades": "skills",
        "experience": "experience",
        "experiencia": "experience"
    }

    @classmethod
    def _normalize_header(cls, raw_header: str) -> str:
        """Limpia los nombres de las columnas, removiendo acentos comunes y convirtiendo a minúsculas."""
        if not raw_header:
            return ""
        
        # Normalización manual básica de caracteres acentuados comunes en cabeceras
        cleaned = raw_header.strip().lower()
        replacements = [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]
        for accent, clean in replacements:
            cleaned = cleaned.replace(accent, clean)
            
        return cls.HEADER_MAPPING.get(cleaned, cleaned)

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validación de estructura de correo electrónico para evitar persistir datos corruptos."""
        if not email:
            return False
        return bool(EMAIL_REGEX.match(email.strip()))

    @classmethod
    def parse_csv(cls, file_bytes: bytes) -> List[Dict[str, Any]]:
        """Parsea y valida un archivo CSV desde su representación en bytes.
        
        Retorna una lista de diccionarios con cabeceras estrictamente normalizadas y datos limpios.
        Levanta un ValueError si el archivo no cumple con el esquema mínimo requerido.
        """
        try:
            # utf-8-sig maneja el BOM (Byte Order Mark) que aplicaciones como Excel añaden al exportar a CSV
            decoded_content = file_bytes.decode("utf-8-sig", errors="ignore")
            csv_file = io.StringIO(decoded_content)
            
            raw_reader = csv.reader(csv_file)
            raw_headers = next(raw_reader, None)
            
            if not raw_headers:
                raise ValueError("El archivo suministrado está vacío o carece de una línea de cabecera.")
            
            # Normalizar todas las cabeceras encontradas
            normalized_headers = [cls._normalize_header(h) for h in raw_headers]
            
            # Validar esquema mínimo requerido por el negocio
            if "name" not in normalized_headers or "email" not in normalized_headers:
                raise ValueError(
                    f"Estructura inválida. Se requiere obligatoriamente una columna de Nombre y otra de Email. "
                    f"Cabeceras detectadas y procesadas: {raw_headers}"
                )
            
            # Reiniciar puntero de StringIO y saltar cabecera original para leer el contenido real
            csv_file.seek(0)
            next(csv_file)
            
            reader = csv.DictReader(csv_file, fieldnames=normalized_headers)
            cleaned_records = []
            
            for row in reader:
                name = (row.get("name") or "").strip()
                email = (row.get("email") or "").strip()
                
                # Validación defensiva de campos críticos (ignorar líneas corruptas de forma silenciosa o registrar en logs)
                if not name:
                    continue
                if not cls.validate_email(email):
                    continue
                
                # Estructura limpia y homogeneizada mapeada al esquema del negocio
                cleaned_candidates = {
                    "name": name,
                    "email": email,
                    "phone": (row.get("phone") or "").strip() or None,
                    "summary": (row.get("summary") or "").strip() or None,
                    "skills": (row.get("skills") or "").strip() or None,
                    "experience": (row.get("experience") or "").strip() or None
                }
                cleaned_records.append(cleaned_candidates)
                
            return cleaned_records
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Fallo de lectura interna en el parser de CSV: {str(e)}")
    
    @classmethod
    def extract_text_from_pdf(cls, file_bytes: bytes) -> str:
        """Extrae el texto plano de un archivo PDF en memoria de forma segura y defensiva."""
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            text_parts = []
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                
            full_text = " ".join(text_parts)
            # Normalizar espacios en blanco redundantes y saltos de línea extraños
            return re.sub(r'\s+', ' ', full_text).strip()
            
        except Exception as e:
            raise ValueError(f"Error procesando la estructura interna del archivo PDF: {str(e)}")

    @classmethod
    def parse_zip_archive(cls, zip_bytes: bytes) -> List[Dict[str, bytes]]:
        """Descomprime un archivo ZIP en memoria y retorna los archivos PDF que contiene."""
        pdf_files = []
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_ref:
                for file_info in zip_ref.infolist():
                    # Ignorar directorios, archivos ocultos y archivos que no tengan extensión .pdf
                    if file_info.is_dir() or file_info.filename.startswith("__") or not file_info.filename.lower().endswith(".pdf"):
                        continue
                    
                    # Extraer el contenido binario del PDF en memoria
                    with zip_ref.open(file_info.filename) as f:
                        pdf_files.append({
                            "filename": file_info.filename,
                            "content": f.read()
                        })
            return pdf_files
        except Exception as e:
            raise ValueError(f"Error al procesar el archivo ZIP comprimido: {str(e)}")