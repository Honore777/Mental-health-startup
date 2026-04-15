import asyncio
import random
from collections.abc import Awaitable, Callable


async def async_retry(
    operation: Callable[[], Awaitable[str]],
    attempts: int,
    base_delay: float,
    max_delay: float,
) -> str:
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return await operation()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == attempts:
                break

            exponential_delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            jitter = random.uniform(0, 0.1)
            await asyncio.sleep(exponential_delay + jitter)

    if last_error is not None:
        raise last_error
    raise RuntimeError("Retry failed without captured exception")
