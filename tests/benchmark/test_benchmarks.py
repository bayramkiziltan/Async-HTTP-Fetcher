"""
Comprehensive benchmark tests for the Async HTTP Fetcher.
These tests measure performance characteristics under different conditions.
"""
import pytest
import asyncio
import time
from unittest.mock import patch
from src.fetcher import fetch_all
from tests.fetcher.test_fetcher_mock import MockResponse, MockResponseAwaitable


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_benchmark_small_batch():
    """Benchmark small batch (10 URLs) processing."""
    urls = [f"https://api.example.com/endpoint/{i}" for i in range(10)]
    mock_response = MockResponse(200, '{"data": "test_response", "id": 1}')
    
    start_time = time.perf_counter()
    
    with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)):
        results = await fetch_all(urls, concurrency=5)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    # Assertions
    assert len(results) == 10
    assert all(result is not None for result in results)
    
    # Performance metrics
    rps = len(results) / duration if duration > 0 else float('inf')
    
    # Save benchmark results
    benchmark_result = f"""
Small Batch Benchmark (10 URLs):
- Duration: {duration:.4f} seconds
- RPS: {rps:.2f} requests/second
- Concurrency: 5
- Success rate: 100%
"""
    
    with open("benchmark-results.txt", "a") as f:
        f.write(benchmark_result + "\n")
    
    print(f"Small batch benchmark: {rps:.2f} RPS in {duration:.4f}s")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_benchmark_medium_batch():
    """Benchmark medium batch (100 URLs) processing."""
    urls = [f"https://api.example.com/endpoint/{i}" for i in range(100)]
    mock_response = MockResponse(200, '{"data": "test_response", "id": 1}')
    
    start_time = time.perf_counter()
    
    with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)):
        results = await fetch_all(urls, concurrency=10)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    # Assertions
    assert len(results) == 100
    assert all(result is not None for result in results)
    
    # Performance metrics
    rps = len(results) / duration if duration > 0 else float('inf')
    
    # Save benchmark results
    benchmark_result = f"""
Medium Batch Benchmark (100 URLs):
- Duration: {duration:.4f} seconds
- RPS: {rps:.2f} requests/second
- Concurrency: 10
- Success rate: 100%
"""
    
    with open("benchmark-results.txt", "a") as f:
        f.write(benchmark_result + "\n")
    
    print(f"Medium batch benchmark: {rps:.2f} RPS in {duration:.4f}s")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_benchmark_large_batch():
    """Benchmark large batch (500 URLs) processing."""
    urls = [f"https://api.example.com/endpoint/{i}" for i in range(500)]
    mock_response = MockResponse(200, '{"data": "test_response", "id": 1}')
    
    start_time = time.perf_counter()
    
    with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)):
        results = await fetch_all(urls, concurrency=20)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    # Assertions
    assert len(results) == 500
    assert all(result is not None for result in results)
    
    # Performance metrics
    rps = len(results) / duration if duration > 0 else float('inf')
    
    # Save benchmark results
    benchmark_result = f"""
Large Batch Benchmark (500 URLs):
- Duration: {duration:.4f} seconds
- RPS: {rps:.2f} requests/second
- Concurrency: 20
- Success rate: 100%
"""
    
    with open("benchmark-results.txt", "a") as f:
        f.write(benchmark_result + "\n")
    
    print(f"Large batch benchmark: {rps:.2f} RPS in {duration:.4f}s")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_benchmark_concurrency_comparison():
    """Benchmark different concurrency levels."""
    urls = [f"https://api.example.com/endpoint/{i}" for i in range(50)]
    mock_response = MockResponse(200, '{"data": "test_response", "id": 1}')
    concurrency_levels = [1, 5, 10, 20, 50]
    
    results_summary = []
    
    for concurrency in concurrency_levels:
        start_time = time.perf_counter()
        
        with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)):
            results = await fetch_all(urls, concurrency=concurrency)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        rps = len(results) / duration if duration > 0 else float('inf')
        
        results_summary.append(f"  Concurrency {concurrency}: {rps:.2f} RPS ({duration:.4f}s)")
        
        # Assertions
        assert len(results) == 50
        assert all(result is not None for result in results)
    
    # Save benchmark results
    benchmark_result = f"""
Concurrency Comparison Benchmark (50 URLs):
{chr(10).join(results_summary)}
"""
    
    with open("benchmark-results.txt", "a") as f:
        f.write(benchmark_result + "\n")
    
    print("Concurrency comparison completed")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_benchmark_error_handling():
    """Benchmark performance with mixed success/error responses."""
    urls = [f"https://api.example.com/endpoint/{i}" for i in range(100)]
    
    async def mock_get_with_errors(url, **kwargs):
        # 70% success, 30% errors
        url_num = int(url.split('/')[-1])
        if url_num % 10 < 7:  # 70% success
            return MockResponseAwaitable(MockResponse(200, '{"data": "success"}'))
        else:  # 30% errors
            return MockResponseAwaitable(MockResponse(500, '{"error": "server_error"}'))
    
    start_time = time.perf_counter()
    
    with patch('aiohttp.ClientSession.get', side_effect=mock_get_with_errors):
        results = await fetch_all(urls, concurrency=10)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    # Count successful vs failed results
    successful = sum(1 for result in results if result is not None and '"error"' not in str(result))
    failed = len(results) - successful
    
    rps = len(results) / duration if duration > 0 else float('inf')
    success_rate = (successful / len(results)) * 100
    
    # Save benchmark results
    benchmark_result = f"""
Error Handling Benchmark (100 URLs, 70/30 success/error):
- Duration: {duration:.4f} seconds
- RPS: {rps:.2f} requests/second
- Success rate: {success_rate:.1f}%
- Successful: {successful}, Failed: {failed}
"""
    
    with open("benchmark-results.txt", "a") as f:
        f.write(benchmark_result + "\n")
    
    print(f"Error handling benchmark: {success_rate:.1f}% success rate")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_benchmark_memory_efficiency():
    """Benchmark memory efficiency with larger response payloads."""
    urls = [f"https://api.example.com/large-data/{i}" for i in range(100)]
    
    # Create a larger mock response (1KB)
    large_data = {"data": "x" * 1000, "metadata": {"size": "1KB"}}
    mock_response = MockResponse(200, str(large_data))
    
    start_time = time.perf_counter()
    
    with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)):
        results = await fetch_all(urls, concurrency=15)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    # Assertions
    assert len(results) == 100
    assert all(result is not None for result in results)
    
    # Performance metrics
    rps = len(results) / duration if duration > 0 else float('inf')
    total_data_size = len(str(large_data)) * len(results)
    throughput_mb = (total_data_size / (1024 * 1024)) / duration if duration > 0 else 0
    
    # Save benchmark results
    benchmark_result = f"""
Memory Efficiency Benchmark (100 URLs, 1KB responses):
- Duration: {duration:.4f} seconds
- RPS: {rps:.2f} requests/second
- Data throughput: {throughput_mb:.2f} MB/s
- Total data processed: {total_data_size / 1024:.1f} KB
"""
    
    with open("benchmark-results.txt", "a") as f:
        f.write(benchmark_result + "\n")
    
    print(f"Memory efficiency benchmark: {throughput_mb:.2f} MB/s throughput")
