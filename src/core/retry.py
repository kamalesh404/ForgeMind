"""Retry decorator with exponential backoff for LLM calls."""

import asyncio
import functools
import logging
import random
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential: bool = True,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Base delay in seconds between retries.
        max_delay: Maximum delay cap in seconds.
        exponential: Whether to use exponential backoff.
        jitter: Whether to add random jitter to delay.
        retryable_exceptions: Tuple of exceptions to catch and retry.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    delay = _compute_delay(attempt, base_delay, max_delay, exponential, jitter)
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}. "
                        f"Waiting {delay:.1f}s"
                    )
                    import time
                    time.sleep(delay)
            raise last_exception

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    delay = _compute_delay(attempt, base_delay, max_delay, exponential, jitter)
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}. "
                        f"Waiting {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)
            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _compute_delay(attempt: int, base: float, max_delay: float, exponential: bool, jitter: bool) -> float:
    if exponential:
        delay = min(base * (2 ** attempt), max_delay)
    else:
        delay = base
    if jitter:
        delay *= random.uniform(0.5, 1.5)
    return min(delay, max_delay)
