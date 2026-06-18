import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log
)

logger = logging.getLogger(__name__)

def create_retry_decorator(max_retries: int = 3, min_seconds: int = 1, max_seconds: int = 10):
    """
    Creates a retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries before giving up.
        min_seconds: Minimum time to wait before retrying (base for exponential).
        max_seconds: Maximum time to wait between retries.
    """
    return retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=min_seconds, min=min_seconds, max=max_seconds),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )

external_api_retry = create_retry_decorator(
    max_retries=3,
    min_seconds=1,
    max_seconds=10
)

db_retry = create_retry_decorator(
    max_retries=5,
    min_seconds=0.5,
    max_seconds=5
)