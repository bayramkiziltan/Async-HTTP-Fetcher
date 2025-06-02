# Performance Benchmark Script

Bu doküman, Async HTTP Fetcher kütüphanesinin performans testleri için kullanılan benchmark scriptini içermektedir.

## 🚀 Benchmark Script

Aşağıdaki script, farklı URL sayıları ve endpoint tiplerinde performans testleri yapar:

```python
import asyncio
import time
from src.fetcher.fetcher import fetch_all

async def quick_benchmark():
    """
    Comprehensive performance benchmark for Async HTTP Fetcher.
    Tests different URL counts and endpoint types to measure:
    - Duration
    - Success rate
    - Throughput
    - Optimal concurrency levels
    """
    print('📊 Real Performance Benchmark Results')
    print('=' * 55)
    
    # Different endpoint types for realistic testing
    endpoints = {
        'fast': 'https://httpbin.org/get',
        'medium': 'https://httpbin.org/delay/0.5',
        'slow': 'https://httpbin.org/delay/1'
    }
    
    test_scenarios = [
        (10, 'fast'),
        (50, 'fast'), 
        (100, 'fast'),
        (10, 'medium'),
        (50, 'medium'),
        (10, 'slow'),
        (25, 'slow')
    ]
    
    print('| URLs | Type   | Duration | Success | Throughput | Concurrency |')
    print('|------|--------|----------|---------|------------|-------------|')
    
    results = []
    
    for url_count, endpoint_type in test_scenarios:
        base_url = endpoints[endpoint_type]
        urls = [base_url] * url_count
        concurrency = min(url_count, 20)  # Reasonable concurrency
        
        start = time.perf_counter()
        responses = await fetch_all(urls, concurrency=concurrency)
        duration = time.perf_counter() - start
        
        success_count = len([r for r in responses if r])
        success_rate = success_count / len(responses) * 100
        throughput = success_count / duration if duration > 0 else 0
        
        # Store results for analysis
        results.append({
            'url_count': url_count,
            'endpoint_type': endpoint_type,
            'duration': duration,
            'success_rate': success_rate,
            'throughput': throughput,
            'concurrency': concurrency
        })
        
        print(f'| {url_count:4d} | {endpoint_type:6s} | {duration:6.2f}s | {success_rate:5.1f}% | {throughput:8.1f}/s | {concurrency:9d} |')
    
    return results

# Run the benchmark
if __name__ == "__main__":
    results = asyncio.run(quick_benchmark())
```

## 📊 Extended Benchmark Script

Daha detaylı analiz için genişletilmiş versiyon:

```python
import asyncio
import time
import statistics
from src.fetcher.fetcher import fetch_all

async def detailed_benchmark():
    """
    Extended benchmark with multiple runs and statistical analysis.
    """
    print('📈 Detailed Performance Analysis')
    print('=' * 60)
    
    endpoints = {
        'fast': 'https://httpbin.org/get',
        'medium': 'https://httpbin.org/delay/0.5',
        'slow': 'https://httpbin.org/delay/1'
    }
    
    test_scenarios = [
        (10, 'fast'),
        (25, 'fast'),
        (50, 'fast'),
        (10, 'medium'),
        (25, 'medium')
    ]
    
    print('| URLs | Type   | Avg Duration | Min | Max | Success | Avg Throughput |')
    print('|------|--------|--------------|-----|-----|---------|----------------|')
    
    for url_count, endpoint_type in test_scenarios:
        base_url = endpoints[endpoint_type]
        urls = [base_url] * url_count
        concurrency = min(url_count, 15)
        
        # Multiple runs for statistical accuracy
        durations = []
        success_rates = []
        throughputs = []
        
        for run in range(3):  # 3 runs
            start = time.perf_counter()
            responses = await fetch_all(urls, concurrency=concurrency)
            duration = time.perf_counter() - start
            
            success_count = len([r for r in responses if r])
            success_rate = success_count / len(responses) * 100
            throughput = success_count / duration if duration > 0 else 0
            
            durations.append(duration)
            success_rates.append(success_rate)
            throughputs.append(throughput)
            
            # Small delay between runs
            await asyncio.sleep(1)
        
        avg_duration = statistics.mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        avg_success = statistics.mean(success_rates)
        avg_throughput = statistics.mean(throughputs)
        
        print(f'| {url_count:4d} | {endpoint_type:6s} | {avg_duration:10.2f}s | {min_duration:3.1f} | {max_duration:3.1f} | {avg_success:5.1f}% | {avg_throughput:12.1f}/s |')

# Run detailed benchmark
if __name__ == "__main__":
    asyncio.run(detailed_benchmark())
```

## 🔧 Usage Instructions

### 1. Basic Benchmark

```bash
cd "/path/to/Async HTTP Fetcher"
python3 -c "
import asyncio
import time
from src.fetcher.fetcher import fetch_all

# ... (yukarıdaki quick_benchmark kodunu buraya yapıştır)

asyncio.run(quick_benchmark())
"
```

### 2. Terminal'den Hızlı Test

```bash
cd "/Users/bayramkiziltan/Documents/GitHub/Async HTTP Fetcher"
python3 -c "
import asyncio
import time
from src.fetcher.fetcher import fetch_all

async def quick_test():
    urls = ['https://httpbin.org/get'] * 10
    start = time.perf_counter()
    responses = await fetch_all(urls, concurrency=10)
    duration = time.perf_counter() - start
    success = len([r for r in responses if r])
    print(f'10 URLs: {duration:.2f}s, Success: {success}/10, Throughput: {success/duration:.1f}/s')

asyncio.run(quick_test())
"
```

### 3. Dosya Olarak Kayıt

Benchmark sonuçlarını dosyaya kaydetmek için:

```python
import json
from datetime import datetime

async def benchmark_with_logging():
    results = await quick_benchmark()
    
    # Save to file
    benchmark_data = {
        'timestamp': datetime.now().isoformat(),
        'environment': 'macOS, Python 3.9+',
        'results': results
    }
    
    with open('logs/benchmark_results.json', 'w') as f:
        json.dump(benchmark_data, f, indent=2)
    
    print(f"\n✅ Results saved to logs/benchmark_results.json")
```

## 📋 Endpoint Types

| Type | URL | Expected Behavior |
|------|-----|-------------------|
| **fast** | `https://httpbin.org/get` | Immediate response |
| **medium** | `https://httpbin.org/delay/0.5` | 0.5 second delay |
| **slow** | `https://httpbin.org/delay/1` | 1 second delay |

## 🎯 Performance Expectations

- **Fast endpoints**: 2-5 req/s sustained throughput
- **Medium delay**: 0.5-2 req/s depending on concurrency
- **Slow endpoints**: 0.3-1 req/s with proper timeout handling
- **Success rates**: 95%+ under normal conditions
- **Optimal concurrency**: 10-20 for most scenarios

## 🔍 Analysis Tips

1. **Throughput**: Higher is better (requests/second)
2. **Success Rate**: Should be >95% for healthy endpoints
3. **Duration**: Should scale sub-linearly with URL count
4. **Concurrency**: Sweet spot usually 10-20 for httpbin.org

## ⚠️ Notes

- Results vary based on network conditions
- httpbin.org rate limiting may affect large tests
- Use local test servers for consistent benchmarking
- Multiple runs recommended for statistical accuracy
