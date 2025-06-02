import logging
from contextlib import contextmanager
import asyncio
import sys
import os
# Ana proje dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import timer, LogConfig, LoggingPolicy
import aiohttp
import time
import json
from typing import Optional, Dict

# Log konfigürasyonunu kaldır - sadece CLI kullanımında yapılacak

class AuthConfig:
    def __init__(self, 
                 auth_url: str,
                 username: str,
                 password: str,
                 token_field: str = "access_token"):
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.token_field = token_field
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}

    async def get_token(self, session: aiohttp.ClientSession) -> bool:
        """JWT token alır ve headers'a ekler"""
        try:
            payload = {
                "username": self.username,
                "password": self.password
            }
            async with session.post(self.auth_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get(self.token_field)
                    if self.token:
                        self.headers = {
                            "Authorization": f"Bearer {self.token}",
                            "Content-Type": "application/json"
                        }
                        logging.info("Token successfully obtained")
                        return True
                    else:
                        logging.error(f"Token field '{self.token_field}' not found in response")
                        return False
                else:
                    logging.error(f"Authentication failed with status code: {response.status}")
                    return False
        except Exception as e:
            logging.error(f"Error during authentication: {e}")
            return False

@timer()
async def _fetch(session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore, 
                concurrency: int, auth_config: AuthConfig = None):
    """
    Fetch a single URL with authentication support
    Args:
        session (aiohttp.ClientSession): The session to use for the request
        url (str): The URL to fetch
        sem (asyncio.Semaphore): Semaphore to limit concurrency
        concurrency (int): Maximum number of concurrent requests
        auth_config (AuthConfig, optional): Authentication configuration
    """
    async with sem:
        available_slots = sem._value
        active_requests = concurrency - available_slots
        try:
            headers = auth_config.headers if auth_config else {}
            logging.info(f"URL: {url} | Aktif İstek: {active_requests}/{concurrency}")
            
            async with session.get(url, headers=headers) as response:
                if response.status == 401 and auth_config:
                    # Token expire olduysa yeniden al
                    if await auth_config.get_token(session):
                        # Yeni token ile tekrar dene
                        headers = auth_config.headers
                        async with session.get(url, headers=headers) as retry_response:
                            if retry_response.status == 200:
                                result = await retry_response.text()
                                logging.info(f"Successfully fetched {url} after token refresh")
                                return result
                elif response.status == 200:
                    result = await response.text()
                    logging.info(f"Successfully fetched {url}")
                    return result
                else:
                    logging.warning(f"Failed to fetch {url} - Status: {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

@timer()
async def fetch_all(urls: list[str], concurrency: int = 100, auth_config: AuthConfig = None):
    """
    Fetch all URLs concurrently with authentication support
    
    Args:
        urls (list[str]): URLs to fetch
        concurrency (int): Maximum concurrent requests
        auth_config (AuthConfig, optional): Authentication configuration
    """
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        if auth_config:
            # İlk token'ı al
            if not await auth_config.get_token(session):
                logging.error("Initial authentication failed")
                return []
        
        tasks = [_fetch(session, url, sem, concurrency, auth_config) for url in urls]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

if __name__ == "__main__":
    # Log konfigürasyonunu sadece CLI kullanımında ayarla
    log_config = LogConfig(
        level=logging.INFO,
        file_path='logs/auth_fetcher.log',
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    LoggingPolicy(log_config)
    
    # Test için örnek konfigürasyon
    auth_config = AuthConfig(
        auth_url="https://api.example.com/auth/login",
        username="test_user",
        password="test_password"
    )
    
    # Test URLs (bu URL'leri kendi API'niz ile değiştirin)
    protected_urls = [
        "https://api.example.com/protected/resource1",
        "https://api.example.com/protected/resource2",
        "https://api.example.com/protected/resource3",
    ] * 5  # Her birinden 5 tane
    
    print("\nTesting authenticated requests:")
    start_time = time.time()
    responses = asyncio.run(fetch_all(protected_urls, concurrency=5, auth_config=auth_config))
    end_time = time.time()
    print(f"Fetched {len(responses)} protected URLs in {end_time - start_time:.2f} seconds")
