import pytest
import logging
from src.utils.context_utils import log_time, LogTime
import time

@pytest.fixture
def mock_logger(caplog):
    caplog.set_level(logging.INFO)
    return logging.getLogger("test")

def test_log_time_normal_execution(mock_logger, caplog):
    with log_time("test_operation", logger=mock_logger):
        time.sleep(0.1)
    
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "test_operation finished in" in record.message
    assert "0.1" in record.message
    assert "exc:" not in record.message

def test_log_time_with_exception(mock_logger, caplog):
    with pytest.raises(ValueError, match="test error"):
        with log_time("error_operation", logger=mock_logger):
            time.sleep(0.1)
            raise ValueError("test error")
    
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "error_operation finished in" in record.message
    assert "0.1" in record.message
    assert "exc: test error" in record.message

def test_log_time_class_normal_execution(mock_logger, caplog):
    with LogTime("test_class", logger=mock_logger):
        time.sleep(0.1)
    
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "test_class finished in" in record.message
    assert "0.1" in record.message
    assert "exc:" not in record.message

def test_log_time_class_with_exception(mock_logger, caplog):
    with pytest.raises(ValueError, match="class error"):
        with LogTime("error_class", logger=mock_logger):
            time.sleep(0.1)
            raise ValueError("class error")
    
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "error_class finished in" in record.message
    assert "0.1" in record.message
    assert "exc: class error" in record.message

def test_nested_log_time(mock_logger, caplog):
    with log_time("outer", logger=mock_logger):
        time.sleep(0.1)
        with log_time("inner", logger=mock_logger):
            time.sleep(0.1)
    
    assert len(caplog.records) == 2
    inner_record = caplog.records[0]
    outer_record = caplog.records[1]
    
    assert "inner finished in" in inner_record.message
    assert "outer finished in" in outer_record.message
    
    inner_time = float(inner_record.message.split("in ")[-1].rstrip("s"))
    outer_time = float(outer_record.message.split("in ")[-1].rstrip("s"))
    assert outer_time > inner_time
