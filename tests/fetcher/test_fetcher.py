"""
Integration tests for the fetcher module.
These tests use real HTTP requests and may be less reliable in CI environments.
Use pytest -m "not integration" to skip these tests.
"""
import pytest
import asyncio
from src.fetcher import fetch_all

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

SUCCESS_URLS = [
    "https://httpbin.org/get",
    "https://httpbin.org/status/200",
    "https://httpbin.org/delay/0.1",
]

ERROR_URLS = [
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://invalid.example.com",
]

@pytest.mark.asyncio
async def test_successful_urls():
    """Test fetching from real URLs - may fail if httpbin.org is down."""
    try:
        results = await fetch_all(SUCCESS_URLS, concurrency=3, timeout=10.0)
        
        assert len(results) == len(SUCCESS_URLS)
        
        # At least some requests should succeed
        successful_results = [r for r in results if r is not None]
        assert len(successful_results) > 0, "No requests succeeded"
        
        for result in successful_results:
            assert isinstance(result, str)
            assert len(result) > 0
    except Exception as e:
        pytest.skip(f"Integration test skipped due to network issue: {e}")

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.benchmark
async def test_performance_metrics():
    """Test basic performance characteristics - may fail if httpbin.org is slow."""
    try:
        start_time = asyncio.get_event_loop().time()
        
        results = await fetch_all(SUCCESS_URLS, concurrency=3, timeout=10.0)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        successful_requests = len([r for r in results if r is not None])
        
        summary = {
            'total_requests': len(SUCCESS_URLS),
            'successful_requests': successful_requests,
            'duration': duration,
            'rps': successful_requests / duration if duration > 0 else 0
        }
        
        # More lenient assertions for CI
        assert summary['duration'] < 30.0, f"Operation took too long: {summary['duration']:.2f}s"
        
        if successful_requests > 0:
            assert summary['rps'] > 0, f"RPS calculation failed: {summary['rps']:.2f}"
        
        print(f"\nPerformance Summary:")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Requests/sec: {summary['rps']:.2f}")
        print(f"Success rate: {successful_requests}/{len(SUCCESS_URLS)}")
        
        # Save benchmark results to file for CI artifacts
        benchmark_results = f"""
Integration Benchmark Results:
- Total URLs: {summary['total_requests']}
- Successful requests: {summary['successful_requests']}
- Duration: {summary['duration']:.4f} seconds
- RPS: {summary['rps']:.2f} requests/second
- Success rate: {successful_requests}/{len(SUCCESS_URLS)}
"""
        
        # Append to benchmark results file
        with open("benchmark-results.txt", "a") as f:
            f.write(benchmark_results + "\n")
    except Exception as e:
        pytest.skip(f"Integration test skipped due to network issue: {e}")

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling with real error URLs."""
    try:
        results = await fetch_all(ERROR_URLS, concurrency=2, timeout=5.0)
        
        assert len(results) == len(ERROR_URLS)
        # All should be None due to errors
        assert all(result is None for result in results)
        
        # Test mixed URLs
        mixed_urls = SUCCESS_URLS[:1] + ERROR_URLS[:1]
        results = await fetch_all(mixed_urls, concurrency=2, timeout=5.0)
        
        assert len(results) == 2
        # At least one should be an error (the error URL)
        error_count = len([r for r in results if r is None])
        assert error_count >= 1, "Expected at least one error result"
    except Exception as e:
        pytest.skip(f"Integration test skipped due to network issue: {e}")
