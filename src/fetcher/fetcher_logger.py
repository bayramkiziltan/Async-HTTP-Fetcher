import logging

class FetcherLogger:
    
    def __init__(self):
        # Kütüphane kullanıcılarının logger konfigürasyonunu etkilememek için
        # sadece logger'ları al, konfigürasyon yapma
        self.request_logger = logging.getLogger("async_fetcher.request")
        self.performance_logger = logging.getLogger("async_fetcher.performance")
        self.error_logger = logging.getLogger("async_fetcher.error")
        
        # Eğer hiç handler yoksa, NullHandler ekle (logging best practice)
        if not self.request_logger.handlers:
            self.request_logger.addHandler(logging.NullHandler())
        if not self.performance_logger.handlers:
            self.performance_logger.addHandler(logging.NullHandler())
        if not self.error_logger.handlers:
            self.error_logger.addHandler(logging.NullHandler())
    
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
