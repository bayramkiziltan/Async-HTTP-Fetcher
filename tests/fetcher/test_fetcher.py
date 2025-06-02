import pytest
import asyncio
from src.fetcher import fetch_all

SUCCESS_URLS = [
    "https://httpbin.org/get",
    "https://httpbin.org/status/200",
    "https://httpbin.org/delay/0.1",
    "https://httpbin.org/delay/0.2",
    "https://httpbin.org/delay/0.3"
]

ERROR_URLS = [
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://invalid.example.com",
]

@pytest.mark.asyncio
async def test_successful_urls():
    results = await fetch_all(SUCCESS_URLS, concurrency=5)
    
    assert len(results) == len(SUCCESS_URLS)
    
    for result in results:
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

@pytest.mark.asyncio
async def test_performance_metrics():
    start_time = asyncio.get_event_loop().time()
    
    results = await fetch_all(SUCCESS_URLS, concurrency=5)
    
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    
    successful_requests = len([r for r in results if r is not None])
    
    summary = {
        'total_requests': len(SUCCESS_URLS),
        'successful_requests': successful_requests,
        'duration': duration,
        'rps': successful_requests / duration
    }
    
    assert summary['duration'] < 15.0, f"İşlem 15 saniyeden uzun sürdü: {summary['duration']:.2f}s"
    assert summary['rps'] > 0.3, f"RPS çok düşük: {summary['rps']:.2f}"
    
    print(f"\nPerformance Summary:")
    print(f"Duration: {summary['duration']:.2f}s")
    print(f"Requests/sec: {summary['rps']:.2f}")
    print(f"Success rate: {successful_requests}/{len(SUCCESS_URLS)}")

@pytest.mark.asyncio
async def test_error_handling():
    results = await fetch_all(ERROR_URLS, concurrency=3)
    
    assert all(result is None for result in results)
    
    mixed_urls = SUCCESS_URLS[:2] + ERROR_URLS[:1] + SUCCESS_URLS[2:3]
    results = await fetch_all(mixed_urls, concurrency=3)
    
    success_count = len([r for r in results if r is not None])
    error_count = len([r for r in results if r is None])
    
    assert success_count == 3
    assert error_count == 1
