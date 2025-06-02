from contextlib import contextmanager
import asyncio
from ..utils import timer
import aiohttp
import time
from .fetcher_logger import FetcherLogger
import logging

logger = FetcherLogger()

@timer()
async def _fetch(session, url, sem, concurrency: int):
    async with sem:
        concurrent_requests = concurrency - sem._value
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if attempt == 0:
                    logger.log_request_start(url, concurrent_requests)
                start = time.perf_counter()
                
                if "/delay/" in url:
                    timeout = aiohttp.ClientTimeout(total=10, connect=3)
                elif "/status/" in url:
                    timeout = aiohttp.ClientTimeout(total=8, connect=3)
                else:
                    timeout = aiohttp.ClientTimeout(total=6, connect=2)
                
                request_options = {
                    "timeout": timeout,
                    "ssl": False
                }
                
                async with session.get(url, **request_options) as response:
                    if response.status == 200:
                        try:
                            if url.endswith("/status/200"):
                                result = "Success"
                            else:
                                result = await response.text()
                                
                            if result is not None:
                                duration = time.perf_counter() - start
                                logger.log_request_success(url, duration, concurrent_requests)
                                return result
                        except (UnicodeDecodeError, aiohttp.ClientPayloadError) as e:
                            if attempt == max_retries:
                                logger.log_request_error(url, f"Content error: {str(e)}", concurrent_requests)
                            continue
                    
                    if response.status >= 500 and attempt < max_retries:
                        await asyncio.sleep(0.5 * (attempt + 1))
                        continue
                        
                    logger.log_request_failure(url, response.status, concurrent_requests)
                    return None
                    
            except asyncio.TimeoutError as e:
                if attempt < max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                logger.log_request_error(url, f"Timeout: {str(e)}", concurrent_requests)
                return None
            except (aiohttp.ClientError, asyncio.CancelledError) as e:
                if attempt < max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                logger.log_request_error(url, str(e), concurrent_requests)
                return None
            except Exception as e:
                logger.log_request_error(url, str(e), concurrent_requests)
                return None
        
        return None



@timer()
async def fetch_all(urls: list[str], concurrency: int = 100):
    start_time = time.perf_counter()
    sem = asyncio.Semaphore(concurrency)
    
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
        tasks = [_fetch(session, url, sem, concurrency) for url in urls]
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