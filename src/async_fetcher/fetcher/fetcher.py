from contextlib import contextmanager
import asyncio
from async_fetcher.utils import timer
import aiohttp
from async_fetcher.fetcher.fetcher_logger import FetcherLogger
from typing import Union, Optional, Tuple
import time

logger = FetcherLogger()

class ConcurrencyTracker:
    """Semaphore wrapper that tracks concurrent requests."""
    
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._active_count = 0
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        await self.semaphore.acquire()
        async with self._lock:
            self._active_count += 1
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        async with self._lock:
            self._active_count -= 1
        self.semaphore.release()
    
    @property
    def active_count(self) -> int:
        """Returns current number of active requests."""
        return self._active_count

def _get_timeout(url: str) -> aiohttp.ClientTimeout:
    """URL'ye göre uygun timeout değerini döndürür."""
    if "/delay/" in url:
        return aiohttp.ClientTimeout(total=10, connect=3)
    elif "/status/" in url:
        return aiohttp.ClientTimeout(total=8, connect=3)
    else:
        return aiohttp.ClientTimeout(total=6, connect=2)

async def _parse_response(url: str, response: aiohttp.ClientResponse) -> Optional[str]:
    """Response'u parse eder ve içeriği döndürür."""
    try:
        if url.endswith("/status/200"):
            return "Success"
        else:
            return await response.text()
    except (UnicodeDecodeError, aiohttp.ClientPayloadError) as e:
        raise aiohttp.ClientPayloadError(f"Content error: {str(e)}")

async def _handle_retry(attempt: int, max_retries: int) -> bool:
    """Retry gerekip gerekmediğini kontrol eder ve bekler."""
    if attempt < max_retries:
        await asyncio.sleep(0.5 * (attempt + 1))
        return True
    return False

async def _make_request(session: aiohttp.ClientSession, url: str, timeout: aiohttp.ClientTimeout) -> aiohttp.ClientResponse:
    """HTTP request yapar ve response döndürür."""
    request_options = {
        "timeout": timeout,
        "ssl": False
    }
    return await session.get(url, **request_options)

async def _process_successful_response(url: str, response: aiohttp.ClientResponse, start_time: float, concurrent_requests: int) -> Optional[str]:
    """200 response'u işler ve sonucu döndürür."""
    try:
        result = await _parse_response(url, response)
        if result is not None:
            duration = time.perf_counter() - start_time
            logger.log_request_success(url, duration, concurrent_requests)
            return result
    except aiohttp.ClientPayloadError as e:
        raise  # Caller'a fırlat, retry için
    return None

async def _handle_response(url: str, response: aiohttp.ClientResponse, start_time: float, concurrent_requests: int, attempt: int, max_retries: int) -> Tuple[Optional[str], bool]:
    """Response'u işler. Returns: (result, should_retry)"""
    if response.status == 200:
        try:
            result = await _process_successful_response(url, response, start_time, concurrent_requests)
            return result, False
        except aiohttp.ClientPayloadError as e:
            if attempt == max_retries:
                logger.log_request_error(url, str(e), concurrent_requests)
                return None, False
            return None, True  # Retry
    
    # Server error - retry if possible
    if response.status >= 500:
        should_retry = await _handle_retry(attempt, max_retries)
        if not should_retry:
            logger.log_request_failure(url, response.status, concurrent_requests)
        return None, should_retry
        
    logger.log_request_failure(url, response.status, concurrent_requests)
    return None, False

async def _single_request_attempt(session: aiohttp.ClientSession, url: str, concurrent_requests: int, attempt: int, max_retries: int) -> Tuple[Optional[str], bool]:
    """Tek bir request denemesi yapar. Returns: (result, should_retry)"""
    try:
        if attempt == 0:
            logger.log_request_start(url, concurrent_requests)
        start_time = time.perf_counter()
        
        timeout = _get_timeout(url)
        
        async with await _make_request(session, url, timeout) as response:
            return await _handle_response(url, response, start_time, concurrent_requests, attempt, max_retries)
            
    except asyncio.TimeoutError as e:
        should_retry = await _handle_retry(attempt, max_retries)
        if not should_retry:
            logger.log_request_error(url, f"Timeout: {str(e)}", concurrent_requests)
        return None, should_retry
        
    except (aiohttp.ClientError, asyncio.CancelledError) as e:
        should_retry = await _handle_retry(attempt, max_retries)
        if not should_retry:
            logger.log_request_error(url, str(e), concurrent_requests)
        return None, should_retry
        
    except Exception as e:
        logger.log_request_error(url, str(e), concurrent_requests)
        return None, False

@timer()
async def _fetch(session: aiohttp.ClientSession, url: str, tracker: ConcurrencyTracker) -> Optional[str]:
    """URL'yi fetch eder, retry logic ile."""
    async with tracker:
        concurrent_requests = tracker.active_count
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            result, should_retry = await _single_request_attempt(
                session, url, concurrent_requests, attempt, max_retries
            )
            
            if result is not None or not should_retry:
                return result
        
        return None



@timer()
async def fetch_all(urls: list[str], concurrency: int = 100) -> list[Optional[str]]:
    start_time = time.perf_counter()
    tracker = ConcurrencyTracker(concurrency)
    
    conn = aiohttp.TCPConnector(
        limit=concurrency * 2,
        ttl_dns_cache=300,
        force_close=False,
        enable_cleanup_closed=True,
        use_dns_cache=True,
        ssl=False
    )
    
    session_config = {
        'connector': conn,
        'timeout': aiohttp.ClientTimeout(total=10, connect=3),
        'raise_for_status': False,
        'connector_owner': True,
    }
    
    async with aiohttp.ClientSession(**session_config) as session:
        tasks = [_fetch(session, url, tracker) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        total_duration = time.perf_counter() - start_time
        success_count = len([r for r in results if r is not None])
        logger.log_batch_performance(
            total_urls=len(urls),
            success_count=success_count,
            total_duration=total_duration,
            concurrency=concurrency
        )
        
        return results


if __name__ == "__main__":
    urls = ["https://httpbin.org/delay/1"] * 20
    
    print("\nTest with high concurrency (20):")
    start_time = time.time()
    responses = asyncio.run(fetch_all(urls, concurrency=20))
    end_time = time.time()
    print(f"High concurrency: Fetched {len(responses)} URLs in {end_time - start_time:.2f} seconds")
    
    print("\nTest with low concurrency (5):")
    start_time = time.time()
    responses = asyncio.run(fetch_all(urls, concurrency=5))
    end_time = time.time()
    print(f"Low concurrency: Fetched {len(responses)} URLs in {end_time - start_time:.2f} seconds")
    
    print("\nTest with sync-like behavior (concurrency=1):")
    start_time = time.time()
    responses = asyncio.run(fetch_all(urls, concurrency=1))
    end_time = time.time()
    print(f"Sync-like: Fetched {len(responses)} URLs in {end_time - start_time:.2f} seconds")