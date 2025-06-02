# Kullanım Rehberi (Usage Guide)

Bu doküman, **Async HTTP Fetcher** kütüphanesinin nasıl kurulacağı, yapılandırılacağı ve çeşitli senaryolarda nasıl kullanılacağı ile ilgili adım adım örnekler sunar.

---

## 📦 Kurulum

1. Proje kök dizinine gidin:
   ```bash
   cd /path/to/python-çalışmalar
   ```
2. Sanal ortam oluşturun ve aktifleştirin (opsiyonel ama önerilir):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. Alternatif olarak `pyproject.toml` kullanıyorsanız:
   ```bash
   pip install .
   ```

---

## ⚙️ Temel Yapılandırma

| Ayar                   | Açıklama                                 | Varsayılan     |
|------------------------|------------------------------------------|----------------|
| `MAX_CONCURRENT`       | Aynı anda yapılacak en fazla istek sayısı | `100`          |
| `HTTP_TIMEOUT`         | İstek zaman aşımı (saniye)               | `30`           |
| `MAX_RETRIES`          | İstemci otomatik yeniden deneme sayısı    | `3`            |
| `BACKOFF_FACTOR`       | Exponential backoff çarpanı              | `1.5`          |
| `LOG_LEVEL`            | Kayıt düzeyi (DEBUG/INFO/WARNING/ERROR)   | `INFO`         |

Bu değerleri ortam değişkenleri veya `src/utils/logging_policy.py` üzerinden ayarlayabilirsiniz.

---

## 🚀 Temel Kullanım

### `fetch_all` Fonksiyonu

Kütüphanenin basit arayüzü:

```python
import asyncio
from src.fetcher.fetcher import AsyncHTTPFetcher

async def main():
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/status/200",
        "https://httpbin.org/delay/1"
    ]

    # AsyncHTTPFetcher nesnesi oluşturun
    fetcher = AsyncHTTPFetcher(
        max_concurrent=10,
        timeout=10,
        max_retries=2,
        backoff_factor=1.0
    )

    # URL listesini fetch edin
    results = await fetcher.fetch_urls(urls)

    # Sonuçları işleyin
    for url, info in results.items():
        if info['success']:
            print(f"✅ {url} → {info['status_code']}")
        else:
            print(f"❌ {url} → {info['error']}")

if __name__ == '__main__':
    asyncio.run(main())
```

- **`results`**: `dict[str, dict]` formatında, her URL için `{ 'success': bool, 'status_code': int, 'body': str, 'error': str }` bilgilerini içerir.

---

## 🛡️ Kimlik Doğrulama (Authentication)

Özel başlık (header) veya token gerektiren API’ler için: 

```python
from src.fetcher.auth_fetcher import AsyncAuthHTTPFetcher
import asyncio

async def main():
    token = "Bearer <YOUR_TOKEN>"
    auth_fetcher = AsyncAuthHTTPFetcher(
        auth_header={'Authorization': token},
        max_concurrent=5
    )

    urls = ["https://api.protected.com/data/1", ...]
    data = await auth_fetcher.fetch_urls(urls)
    print(data)

asyncio.run(main())
```

Kullanılabilir parametreler:
- `auth_header`: `dict` tipinde, `{'Authorization': ...}` veya farklı başlıklar
- Tüm `AsyncHTTPFetcher` parametreleri aynen geçerlidir.

---

## ⏱️ Zaman Ölçme (Timing)

### Dekoratör (Decorator)

Fonksiyon seviyesinde otomatik süre ölçümü:
```python
from src.utils.timer import timer

@timer(log_level=logging.DEBUG)
async def fetch_with_timing():
    # kodunuz...
    await asyncio.sleep(0.2)
    return True

# Çalıştırma
import asyncio; asyncio.run(fetch_with_timing())
``` 

### Context Manager

İhtiyaç duyduğunuz blokları sarmak için:
```python
from src.utils.context_utils import timer
import asyncio

async def workflow():
    async with timer("Setup"):
        await asyncio.sleep(0.1)
    async with timer("Processing"):
        await asyncio.sleep(0.2)

asyncio.run(workflow())
```

---

## 📈 İleri Düzey Kullanım

- **Büyük Veri Setleri** (`100k+ URL`): Batch işleme
  ```python
  async def batch_fetch(urls, batch_size=500):
      all_results = {}
      for i in range(0, len(urls), batch_size):
          batch = urls[i:i+batch_size]
          results = await fetcher.fetch_urls(batch)
          all_results.update(results)
      return all_results
  ```

- **Özel Bağlantı Havuzu Ayarları**:
  ```python
  import aiohttp
  connector = aiohttp.TCPConnector(limit=200, ttl_dns_cache=300)
  fetcher = AsyncHTTPFetcher(connector=connector)
  ```

- **Logging Policy Değiştirme**:
  ```python
  from src.utils.logging_policy import setup_logger
  setup_logger(level="DEBUG", format_string="%(asctime)s %(levelname)s: %(message)s")
  ```

---

## 🧪 Test & Geliştirme

- Tüm testleri çalıştır:
  ```bash
  pytest -v
  ```
- Salt utils testi:
  ```bash
  pytest tests/utils/ -v
  ```

---

## 📚 Ek Kaynaklar

- [API Referansı](API.md)  
- [Teknik Dokümantasyon](TECHNICAL_DOCUMENTATION.md)  
- [Context vs Decorator Karşılaştırması](decorator_vs_context.md)  
- [Performans Olanakları](BENCHMARKS.md)

---

Bu kılavuz projenin en yaygın kullanım senaryolarını kapsar. Daha fazla örnek için `examples/` klasörüne bakabilirsiniz.
