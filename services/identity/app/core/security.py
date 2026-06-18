import asyncio
import bcrypt

def _sync_hash_password(plain_password: str) -> str:
    """Implementación criptográfica síncrona interna."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def _sync_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificación criptográfica síncrona interna."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

async def hash_password(plain_password: str) -> str:
    """Genera el hash de forma asíncrona delegando el procesamiento intensivo de CPU a un pool de hilos."""
    return await asyncio.to_thread(_sync_hash_password, plain_password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Valida la contraseña de forma asíncrona liberando el bucle de eventos."""
    return await asyncio.to_thread(_sync_verify_password, plain_password, hashed_password)