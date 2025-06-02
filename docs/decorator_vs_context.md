# Dekoratör vs Context Manager Kıyaslaması

| Kriter | Dekoratör | Context Manager |
|--------|-----------|----------------|
| Çoklu kod bloğu | ❌ Tek bir fonksiyona uygulanabilir | ✅ with bloğu içinde birden fazla işlem yapılabilir |
| Fonksiyon süsleme | ✅ Fonksiyonun davranışını doğrudan değiştirebilir | ❌ Fonksiyonu doğrudan değiştiremez |
| API sadeliği | ✅ @decorator sözdizimi çok sade | ❌ with ifadesi biraz daha detaylı |
| Kaynak yönetimi | ❌ Kaynakları otomatik temizleyemez | ✅ __enter__/__exit__ ile temiz kaynak yönetimi |
| Hata yönetimi | ❌ Try/except blokları gerekebilir | ✅ __exit__ ile otomatik hata yönetimi |
| Tekrar kullanım | ❌ Her fonksiyon için ayrı dekorasyon gerekir | ✅ Aynı with bloğunda birden çok kez kullanılabilir |

### Açıklamalar:

1. **Çoklu kod bloğu**: Context manager'lar with bloğu içinde birden fazla işlem yapılmasına izin verirken, dekoratörler sadece tek bir fonksiyonu süsleyebilir.

2. **Fonksiyon süsleme**: Dekoratörler fonksiyonun kendisini değiştirebildiği için daha güçlü bir fonksiyon modifikasyonu sağlar.

3. **API sadeliği**: Dekoratörlerin @decorator sözdizimi çok sade ve anlaşılırken, context manager'ların with ifadesi biraz daha detaylı yazım gerektirir.

4. **Kaynak yönetimi**: Context manager'lar __enter__ ve __exit__ metodları sayesinde kaynakların otomatik temizlenmesini sağlar.

5. **Hata yönetimi**: Context manager'lar __exit__ metodu sayesinde otomatik hata yönetimi sağlar, dekoratörlerde bu işi manuel yapmak gerekebilir.

6. **Tekrar kullanım**: Context manager'lar aynı with bloğu içinde birden fazla kez kullanılabilirken, dekoratörler her fonksiyon için ayrı uygulanmalıdır.
