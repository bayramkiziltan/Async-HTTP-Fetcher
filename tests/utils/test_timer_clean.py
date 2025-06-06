import asyncio
import logging
import pytest
import time
from unittest.mock import patch, MagicMock
from async_fetcher import timer

@pytest.fixture
def mock_logger():
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger  

@pytest.mark.asyncio
async def test_async_timer(mock_logger):
    @timer(log_level=logging.DEBUG)
    async def async_function(x):
        await asyncio.sleep(0.1)
        return x * 2

    result = await async_function(5)
    assert result == 10
    mock_logger.log.assert_called_once()
    log_message = mock_logger.log.call_args[0][1]
    assert "[async] async_function took" in log_message

@pytest.mark.asyncio
async def test_sync_timer(mock_logger):
    @timer(log_level=logging.DEBUG)
    def sync_function(x):
        time.sleep(0.1)
        return x * 2

    result = sync_function(5)
    assert result == 10
    mock_logger.log.assert_called_once()
    log_message = mock_logger.log.call_args[0][1]
    assert "sync_function took" in log_message

@pytest.mark.asyncio
async def test_async_timer_no_log_level(mock_logger):
    @timer()
    async def async_function(x):
        await asyncio.sleep(0.1)
        return x * 2

    result = await async_function(5)
    assert result == 10
    mock_logger.log.assert_called_once()
    log_message = mock_logger.log.call_args[0][1]
    assert "[async] async_function took" in log_message

@pytest.mark.asyncio
async def test_sync_timer_no_log_level(mock_logger):
    @timer()
    def sync_function(x):
        time.sleep(0.1)
        return x * 2

    result = sync_function(5)
    assert result == 10
    mock_logger.log.assert_called_once()
    log_message = mock_logger.log.call_args[0][1]
    assert "sync_function took" in log_message

@pytest.mark.asyncio
async def test_timer_decorator_with_exception(mock_logger):
    @timer(log_level=logging.ERROR)
    async def async_function_with_error(x):
        await asyncio.sleep(0.1)
        raise ValueError("An error occurred")

    with pytest.raises(ValueError, match="An error occurred"):
        await async_function_with_error(5)

    mock_logger.log.assert_called_once()
    log_message = mock_logger.log.call_args[0][1]
    assert "[async] async_function_with_error took" in log_message

@pytest.mark.asyncio
async def test_sync_timer_decorator_with_exception(mock_logger):
    @timer(log_level=logging.ERROR)
    def sync_function_with_error(x):
        time.sleep(0.1)
        raise ValueError("An error occurred")

    with pytest.raises(ValueError, match="An error occurred"):
        sync_function_with_error(5)

    mock_logger.log.assert_called_once()
    log_message = mock_logger.log.call_args[0][1]
    assert "sync_function_with_error took" in log_message
