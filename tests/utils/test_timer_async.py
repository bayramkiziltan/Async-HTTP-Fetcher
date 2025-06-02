import asyncio
import logging
import pytest
import time
from async_fetcher import timer


@pytest.mark.asyncio
async def test_sync_function_measurement(caplog):
    """Sync fonksiyon ölçümü (0.1 s sleep) - caplog ile log kontrolü"""
    with caplog.at_level(logging.INFO):
        @timer()
        def sync_function():
            time.sleep(0.1)
            return "sync_done"

        result = sync_function()
        
        # Sonuç kontrolü
        assert result == "sync_done"
        
        # Log satırı var mı kontrol et
        assert len(caplog.records) == 1
        log_message = caplog.records[0].message
        assert "sync_function took" in log_message
        assert "0.1" in log_message  # Yaklaşık 0.1 saniye sürmeli


@pytest.mark.asyncio
async def test_async_function_measurement(caplog):
    """Async fonksiyon ölçümü (0.05 s sleep) - caplog ile log kontrolü"""
    with caplog.at_level(logging.INFO):
        @timer()
        async def async_function():
            await asyncio.sleep(0.05)
            return "async_done"

        result = await async_function()
        
        # Sonuç kontrolü
        assert result == "async_done"
        
        # Log satırı var mı kontrol et
        assert len(caplog.records) == 1
        log_message = caplog.records[0].message
        assert "[async] async_function took" in log_message
        assert "0.05" in log_message  # Yaklaşık 0.05 saniye sürmeli


@pytest.mark.asyncio
async def test_sync_and_async_timing_comparison(caplog):
    """Sync ve async fonksiyonları karşılaştırmalı test"""
    with caplog.at_level(logging.INFO):
        @timer()
        def sync_func():
            time.sleep(0.1)
            return "sync"

        @timer()
        async def async_func():
            await asyncio.sleep(0.05)
            return "async"

        # Her iki fonksiyonu test et
        sync_result = sync_func()
        async_result = await async_func()
        
        # Sonuçları kontrol et
        assert sync_result == "sync"
        assert async_result == "async"
        
        # 2 log kaydı olmalı
        assert len(caplog.records) == 2
        
        # İlk log (sync)
        sync_log = caplog.records[0].message
        assert "sync_func took" in sync_log
        assert "[async]" not in sync_log  # Sync fonksiyonda [async] etiketi olmamalı
        
        # İkinci log (async)
        async_log = caplog.records[1].message
        assert "[async] async_func took" in async_log


@pytest.mark.asyncio
async def test_multiple_async_calls_with_different_timings(caplog):
    """Farklı sürelerde async fonksiyonları test et"""
    with caplog.at_level(logging.INFO):
        @timer()
        async def fast_async():
            await asyncio.sleep(0.02)
            return "fast"

        @timer()
        async def medium_async():
            await asyncio.sleep(0.05)
            return "medium"

        @timer()
        async def slow_async():
            await asyncio.sleep(0.1)
            return "slow"

        # Tüm fonksiyonları çalıştır
        fast_result = await fast_async()
        medium_result = await medium_async()
        slow_result = await slow_async()
        
        # Sonuçları kontrol et
        assert fast_result == "fast"
        assert medium_result == "medium"
        assert slow_result == "slow"
        
        # 3 log kaydı olmalı
        assert len(caplog.records) == 3
        
        # Her log'da [async] etiketi olmalı
        for record in caplog.records:
            assert "[async]" in record.message
            assert "took" in record.message


@pytest.mark.asyncio
async def test_exception_handling_with_timing(caplog):
    """Exception durumunda timing'in çalışıp çalışmadığını test et"""
    with caplog.at_level(logging.INFO):
        @timer()
        async def async_with_exception():
            await asyncio.sleep(0.05)
            raise ValueError("Test exception")

        # Exception fırlatılsa bile timing çalışmalı
        with pytest.raises(ValueError, match="Test exception"):
            await async_with_exception()
        
        # Log kaydı olmalı (exception'a rağmen)
        assert len(caplog.records) == 1
        log_message = caplog.records[0].message
        assert "[async] async_with_exception took" in log_message


@pytest.mark.asyncio
async def test_concurrent_async_functions(caplog):
    """Concurrent async fonksiyonları test et"""
    with caplog.at_level(logging.INFO):
        @timer()
        async def concurrent_func(duration, name):
            await asyncio.sleep(duration)
            return f"completed_{name}"

        # Eş zamanlı çalıştır
        tasks = [
            concurrent_func(0.03, "task1"),
            concurrent_func(0.05, "task2"),
            concurrent_func(0.02, "task3")
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Sonuçları kontrol et
        assert len(results) == 3
        assert "completed_task1" in results
        assert "completed_task2" in results
        assert "completed_task3" in results
        
        # 3 log kaydı olmalı
        assert len(caplog.records) == 3
        
        # Her log'da timing bilgisi olmalı
        for record in caplog.records:
            assert "[async] concurrent_func took" in record.message