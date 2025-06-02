from ..utils import LogConfig, LoggingPolicy
import logging
from pathlib import Path

class FetcherLogger:
    
    def __init__(self):
        self.policy = LoggingPolicy(LogConfig(
            level=logging.INFO,
            file_path="logs/app.log",
            format=(
                "%(asctime)s [%(levelname)s] "
                "%(name)s - %(message)s"
            ),
            console_output=True
        ))
        
        self.request_logger = self.policy.get_logger("fetcher.request")
        self.performance_logger = self.policy.get_logger("fetcher.performance")
        self.error_logger = self.policy.get_logger("fetcher.error")
    
    def log_request_start(self, url: str, concurrent_requests: int):
        """İstek başlangıcını logla"""
        self.request_logger.info(
            f"Starting request to {url} (concurrent requests: {concurrent_requests})"
        )
    
    def log_request_success(self, url: str, duration: float, concurrent_requests: int):
        """Başarılı isteği logla"""
        self.request_logger.info(
            f"Successfully fetched {url} in {duration:.4f}s (concurrent requests: {concurrent_requests})"
        )
    
    def log_request_failure(self, url: str, status_code: int, concurrent_requests: int):
        """Başarısız isteği logla"""
        self.error_logger.warning(
            f"Failed to fetch {url} - Status code: {status_code} (concurrent requests: {concurrent_requests})"
        )
    
    def log_request_error(self, url: str, error: str, concurrent_requests: int):
        """İstek hatasını logla"""
        self.error_logger.error(
            f"Error fetching {url}: {error} (concurrent requests: {concurrent_requests})"
        )
    
    def log_batch_performance(self, total_urls: int, success_count: int, 
                            total_duration: float, concurrency: int):
        """Toplu istek performansını logla"""
        rps = success_count / total_duration if total_duration > 0 else 0
        self.performance_logger.info(
            f"Batch completed: {success_count}/{total_urls} URLs in {total_duration:.2f}s "
            f"(RPS: {rps:.2f}, concurrency: {concurrency})"
        )
