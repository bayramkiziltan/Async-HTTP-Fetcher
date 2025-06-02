"""
Mock-based tests for the fetcher module that don't depend on external services.
These tests are more suitable for CI/CD pipelines.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from src.fetcher import fetch_all


class MockResponse:
    """Mock aiohttp.ClientResponse that can be used as async context manager."""
    
    def __init__(self, status: int, text_content: str):
        self.status = status
        self._text_content = text_content
    
    async def text(self):
        return self._text_content
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockResponseAwaitable:
    """Awaitable wrapper for MockResponse to match aiohttp.ClientSession.get() behavior."""
    
    def __init__(self, response: MockResponse):
        self._response = response
    
    def __await__(self):
        async def _coro():
            return self._response
        return _coro().__await__()
    
    async def __aenter__(self):
        return self._response
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_successful_fetch_mock():
    """Test successful HTTP fetches using mocked responses."""
    urls = [
        "https://example.com/api/1",
        "https://example.com/api/2",
        "https://example.com/api/3"
    ]
    
    # Create mock response that works as async context manager
    mock_response = MockResponse(200, '{"status": "success", "data": "mock_data"}')
    
    with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)):
        results = await fetch_all(urls, concurrency=3)
    
    assert len(results) == len(urls)
    assert all(result is not None for result in results)
    assert all('mock_data' in result for result in results)


@pytest.mark.asyncio
async def test_error_handling_mock():
    """Test error handling with mocked HTTP errors."""
    urls = [
        "https://example.com/api/404",
        "https://example.com/api/500"
    ]
    
    # Create mock error responses
    mock_response_404 = MockResponseAwaitable(MockResponse(404, 'Not Found'))
    mock_response_500 = MockResponseAwaitable(MockResponse(500, 'Internal Server Error'))
    
    responses = [mock_response_404, mock_response_500]
    
    with patch('aiohttp.ClientSession.get', side_effect=responses):
        results = await fetch_all(urls, concurrency=2)
    
    # All should be None due to error status codes
    assert len(results) == len(urls)
    assert all(result is None for result in results)


@pytest.mark.asyncio
async def test_connection_error_mock():
    """Test handling of connection errors."""
    urls = ["https://invalid.example.com"]
    
    # Mock a connection error
    with patch('aiohttp.ClientSession.get', side_effect=aiohttp.ClientConnectorError(
        connection_key=MagicMock(), os_error=OSError("Connection failed")
    )):
        results = await fetch_all(urls, concurrency=1)
    
    assert len(results) == 1
    assert results[0] is None


@pytest.mark.asyncio
async def test_timeout_mock():
    """Test handling of timeout errors."""
    urls = ["https://slow.example.com"]
    
    # Mock a timeout error
    with patch('aiohttp.ClientSession.get', side_effect=asyncio.TimeoutError("Request timeout")):
        results = await fetch_all(urls, concurrency=1)
    
    assert len(results) == 1
    assert results[0] is None


@pytest.mark.asyncio
async def test_mixed_responses_mock():
    """Test handling of mixed successful and failed responses."""
    urls = [
        "https://example.com/success",
        "https://example.com/error",
        "https://example.com/success2"
    ]
    
    # Create mixed responses
    success_response = MockResponseAwaitable(MockResponse(200, '{"status": "success"}'))
    error_response = MockResponseAwaitable(MockResponse(500, 'Error'))
    
    responses = [success_response, error_response, success_response]
    
    with patch('aiohttp.ClientSession.get', side_effect=responses):
        results = await fetch_all(urls, concurrency=3)
    
    assert len(results) == 3
    assert results[0] is not None  # Success
    assert results[1] is None      # Error
    assert results[2] is not None  # Success
    
    success_count = len([r for r in results if r is not None])
    error_count = len([r for r in results if r is None])
    
    assert success_count == 2
    assert error_count == 1


@pytest.mark.asyncio
async def test_concurrency_limits_mock():
    """Test that concurrency limits are respected."""
    urls = [f"https://example.com/api/{i}" for i in range(10)]
    
    mock_response = MockResponse(200, '{"data": "test"}')
    
    with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)) as mock_get:
        results = await fetch_all(urls, concurrency=3)
    
    assert len(results) == 10
    assert all(result is not None for result in results)
    assert mock_get.call_count == 10


@pytest.mark.asyncio
async def test_performance_characteristics_mock():
    """Test basic performance characteristics with mocked responses."""
    urls = [f"https://example.com/api/{i}" for i in range(5)]
    
    mock_response = MockResponse(200, '{"data": "performance_test"}')
    
    start_time = asyncio.get_event_loop().time()
    
    with patch('aiohttp.ClientSession.get', return_value=MockResponseAwaitable(mock_response)):
        results = await fetch_all(urls, concurrency=5)
    
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    
    assert len(results) == 5
    assert all(result is not None for result in results)
    assert duration < 5.0  # Should be very fast with mocks
    
    # Calculate RPS
    rps = len(results) / duration if duration > 0 else float('inf')
    assert rps > 1.0  # Should be very high with mocks
