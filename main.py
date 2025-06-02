from async_fetcher import LoggingPolicy, LogConfig, fetch_all
import logging
import asyncio
import time

async def main():
    log_config = LogConfig(
        level=logging.INFO,
        file_path="logs/app.log",
        console_output=True,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        date_format="%Y-%m-%d %H:%M:%S"
    )
    
    logging_policy = LoggingPolicy(log_config)
    logger = logging_policy.get_logger("main")
    
    logger.info("Uygulama başlatıldı")
    
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
    ]
    
    try:
        for concurrency in [1, 3, 5]:
            logger.info(f"\nTesting with concurrency={concurrency}:")
            start_time = time.time()
            responses = await fetch_all(urls, concurrency=concurrency)
            end_time = time.time()
            
            success_count = len([r for r in responses if r is not None])
            failed_count = len(urls) - success_count
            
            logger.info(
                f"Completed in {end_time - start_time:.2f} seconds:\n"
                f"- Success: {success_count}\n"
                f"- Failed: {failed_count}\n"
                f"- Average time per URL: {(end_time - start_time) / len(urls):.2f} seconds"
            )
    
    except Exception as e:
        logger.error(f"Bir hata oluştu: {e}", exc_info=True)
    
    logger.info("Uygulama sonlandırıldı")

if __name__ == "__main__":
    asyncio.run(main())
