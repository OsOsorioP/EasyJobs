import asyncio
from typing import Optional
from langchain_cohere import ChatCohere
from app.core.config import settings
from app.etl.parser import ETLParser
from app.vector_db.indexer import VectorIndexer
from app.schemas.extracted_candidate import ExtractedCandidate
import httpx

class ETLPipeline:
    @staticmethod
    def run_csv_ingestion(file_content: bytes) -> dict:
        """Orquesta el flujo de ingesta masiva consumiendo los datos pre-procesados por el parser."""
        
        # 1. Delegar lectura y validación estricta al Parser
        candidates_to_process = ETLParser.parse_csv(file_content)
        
        candidates_to_index = []
        processed_count = 0
        
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        with httpx.Client(timeout=30.0, limits=limits) as http_client:
            for candidate_payload in candidates_to_process:
                try:
                    # 2. Registrar candidato en la API del servicio relacional (PostgreSQL)
                    url = f"{settings.CANDIDATE_SERVICE_INTERNAL_URL}/api/v1/candidates"
                    response = http_client.post(url, json=candidate_payload)
                    
                    if response.status_code == 409:
                        continue  # Omitir duplicados de email
                        
                    response.raise_for_status()
                    candidate_db = response.json()
                    
                    # 3. Preparar el texto enriquecido para el modelo de embeddings
                    text_for_embedding = (
                        f"Nombre: {candidate_db['name']}. "
                        f"Habilidades: {candidate_db.get('skills', '')}. "
                        f"Resumen: {candidate_db.get('summary', '')}"
                    )
                    
                    # 4. Formatear para el indexador vectorial de Qdrant
                    candidates_to_index.append({
                        "id": candidate_db["id"],
                        "text_to_vectorize": text_for_embedding,
                        "metadata": {
                            "name": candidate_db["name"],
                            "email": candidate_db["email"]
                        }
                    })
                    
                    # Carga en lotes (batching) cada 50 registros
                    if len(candidates_to_index) >= 50:
                        VectorIndexer.upsert_candidates_to_vector_db(candidates_to_index)
                        processed_count += len(candidates_to_index)
                        candidates_to_index.clear()
                        
                except Exception:
                    continue  # Tolerar fallos de inserción individual para asegurar la continuidad de la carga masiva
            
            # Cargar los elementos remanentes del último bloque
            if candidates_to_index:
                VectorIndexer.upsert_candidates_to_vector_db(candidates_to_index)
                processed_count += len(candidates_to_index)
                
        return {"status": "completed", "total_records_ingested": processed_count}
    
    @staticmethod
    async def _extract_candidate_metadata_with_llm(raw_text: str) -> Optional[ExtractedCandidate]:
        """Utiliza el LLM de Cohere para extraer la metadata del candidato de forma estructurada."""
        try:
            # Command-R está optimizado para extracción de información estructurada y JSON
            llm = ChatCohere(model="command-r-plus", temperature=0.0)
            structured_llm = llm.with_structured_output(ExtractedCandidate)
            
            system_prompt = (
                "Eres un asistente de reclutamiento de IA. Analiza el texto de la siguiente hoja de vida (CV) "
                "y extrae la información requerida de manera estricta y profesional."
            )
            
            # Ejecutar de manera asíncrona no bloqueante
            result = await asyncio.to_thread(
                structured_llm.invoke,
                [("system", system_prompt), ("human", raw_text)]
            )
            return result
        except Exception:
            # En producción, registramos el fallo de extracción del modelo de IA en el logger de auditoría
            return None

    @staticmethod
    async def run_zip_pdf_ingestion(zip_content: bytes) -> dict:
        """Descomprime un ZIP, procesa cada hoja de vida en PDF con IA e indexa los datos."""
        
        # 1. Obtener la lista de archivos PDF dentro del ZIP
        pdf_files = ETLParser.parse_zip_archive(zip_content)
        
        processed_count = 0
        candidates_to_index = []
        
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(timeout=30.0, limits=limits) as http_client:
            for pdf_file in pdf_files:
                try:
                    # 2. Extracción rápida de texto plano del PDF
                    raw_text = ETLParser.extract_text_from_pdf(pdf_file["content"])
                    if not raw_text or len(raw_text) < 50:
                        continue # Evitar procesar archivos vacíos o corruptos
                    
                    # 3. Estructuración inteligente usando el LLM
                    extracted: ExtractedCandidate = await ETLPipeline._extract_candidate_metadata_with_llm(raw_text)
                    if not extracted:
                        continue # Ignorar si el modelo no pudo parsear datos obligatorios (ej. falta email)
                    
                    candidate_payload = extracted.model_dump()
                    
                    # 4. Registrar en PostgreSQL (Servicio de Candidatos) de forma asíncrona
                    url = f"{settings.CANDIDATE_SERVICE_INTERNAL_URL}/api/v1/candidates"
                    response = await http_client.post(url, json=candidate_payload)
                    
                    if response.status_code == 409:
                        continue # Omitir duplicados de correos
                        
                    response.raise_for_status()
                    candidate_db = response.json()
                    
                    # 5. Generar payload para indexar en Qdrant
                    # Nota: Guardamos un payload simplificado en Qdrant pero generamos el embedding 
                    # sobre todo el texto estructurado del candidato
                    text_for_embedding = (
                        f"Nombre: {candidate_db['name']}. "
                        f"Habilidades: {candidate_db.get('skills', '')}. "
                        f"Resumen: {candidate_db.get('summary', '')}"
                    )
                    
                    candidates_to_index.append({
                        "id": candidate_db["id"],
                        "text_to_vectorize": text_for_embedding,
                        "metadata": {
                            "name": candidate_db["name"],
                            "email": candidate_db["email"]
                        }
                    })
                    
                    # Sincronización en lotes de Qdrant (batching de 20 para evitar limites de tasa de Tokens)
                    if len(candidates_to_index) >= 20:
                        # Ejecutar la operación sincrónica de vectorización en hilos de ejecución secundarios
                        await asyncio.to_thread(VectorIndexer.upsert_candidates_to_vector_db, candidates_to_index)
                        processed_count += len(candidates_to_index)
                        candidates_to_index.clear()
                        
                except Exception:
                    # Garantiza que el fallo en la lectura o extracción de un PDF individual 
                    # no sabotee o detenga la carga del resto del ZIP masivo
                    continue
            
            # Cargar elementos remanentes
            if candidates_to_index:
                await asyncio.to_thread(VectorIndexer.upsert_candidates_to_vector_db, candidates_to_index)
                processed_count += len(candidates_to_index)
                
        return {"status": "completed", "total_pdfs_processed": processed_count}