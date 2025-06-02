import asyncio
import logging
import pytest
import time
from unittest.mock import patch, MagicMock
from src.utils.timer import timer

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
