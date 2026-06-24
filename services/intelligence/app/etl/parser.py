import csv
import io
import logging
import re
import zipfile
from typing import Any, Dict, List

from pypdf import PdfReader

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ETLParser:
    """Reads, normalizes, and defensively validates raw input files."""

    HEADER_MAPPING: Dict[str, str] = {
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
        "experiencia": "experience",
    }

    @classmethod
    def _normalize_header(cls, raw_header: str) -> str:
        if not raw_header:
            return ""
        cleaned = raw_header.strip().lower()
        for accent, plain in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
            cleaned = cleaned.replace(accent, plain)
        return cls.HEADER_MAPPING.get(cleaned, cleaned)

    @classmethod
    def validate_email(cls, email: str) -> bool:
        if not email:
            return False
        return bool(EMAIL_REGEX.match(email.strip()))

    @classmethod
    def parse_csv(cls, file_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Parses a CSV from bytes into a list of normalized candidate dicts.

        Raises ValueError for structural issues; silently skips rows with missing
        required fields (name/email) and logs a warning for observability.
        """
        try:
            decoded = file_bytes.decode("utf-8-sig", errors="ignore")
            csv_file = io.StringIO(decoded)

            raw_reader = csv.reader(csv_file)
            raw_headers = next(raw_reader, None)
            if not raw_headers:
                raise ValueError("El archivo está vacío o carece de cabecera.")

            normalized_headers = [cls._normalize_header(h) for h in raw_headers]

            if "name" not in normalized_headers or "email" not in normalized_headers:
                raise ValueError(
                    f"Estructura inválida. Se requieren columnas de nombre y email. "
                    f"Cabeceras detectadas: {raw_headers}"
                )

            csv_file.seek(0)
            next(csv_file)  # skip original header line

            reader = csv.DictReader(csv_file, fieldnames=normalized_headers)
            records: List[Dict[str, Any]] = []

            for row_num, row in enumerate(reader, start=2):
                name = (row.get("name") or "").strip()
                email = (row.get("email") or "").strip()

                if not name:
                    logger.warning("CSV row %d: skipped — missing name", row_num)
                    continue
                if not cls.validate_email(email):
                    logger.warning("CSV row %d: skipped — invalid email '%s'", row_num, email)
                    continue

                records.append(
                    {
                        "name": name,
                        "email": email,
                        "phone": (row.get("phone") or "").strip() or None,
                        "summary": (row.get("summary") or "").strip() or None,
                        "skills": (row.get("skills") or "").strip() or None,
                        "experience": (row.get("experience") or "").strip() or None,
                    }
                )

            return records

        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Error interno en el parser de CSV: {exc}") from exc

    @classmethod
    def extract_text_from_pdf(cls, file_bytes: bytes) -> str:
        """Extracts and normalizes plain text from a PDF in memory."""
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            parts = [page.extract_text() or "" for page in reader.pages]
            full_text = " ".join(parts)
            return re.sub(r"\s+", " ", full_text).strip()
        except Exception as exc:
            raise ValueError(f"Error procesando el PDF: {exc}") from exc

    @classmethod
    def parse_zip_archive(cls, zip_bytes: bytes) -> List[Dict[str, bytes]]:
        """Extracts PDF files from a ZIP archive in memory."""
        pdf_files: List[Dict[str, bytes]] = []
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                for info in zf.infolist():
                    if (
                        info.is_dir()
                        or info.filename.startswith("__")
                        or not info.filename.lower().endswith(".pdf")
                    ):
                        continue
                    with zf.open(info.filename) as f:
                        pdf_files.append({"filename": info.filename, "content": f.read()})
            return pdf_files
        except Exception as exc:
            raise ValueError(f"Error procesando el archivo ZIP: {exc}") from exc