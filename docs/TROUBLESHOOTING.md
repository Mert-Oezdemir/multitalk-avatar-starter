# Sorun giderme

| Belirti | Kontrol |
| --- | --- |
| `API format` uyarısı | ComfyUI'den API-format JSON export edin; normal canvas/workflow JSON farklıdır. |
| `Node/alan eşleşmesi yok` | `inspect-workflow` ile gerçek node ID ve alan adlarını görün. |
| `input klasoru bulunamadi` | `--comfy-root` ile gerçek ComfyUI kökünü gösterin. |
| `Connection refused` | ComfyUI çalışıyor mu? Varsayılan `127.0.0.1:8188` mi? |
| Model bulunamadı | `models/` altındaki dosya yollarını ve workflow seçimini upstream örneğe göre doğrulayın. |
| Yetersiz VRAM | Resmî workflow'daki düşük VRAM/offload ayarlarını ve kısa süreleri deneyin. |
| Ses eşleşmiyor | Ses temizliğini, örnekleme hızını, konuşmacı eşlemesini, süreyi kontrol edin. |
| CLI çıktı vermedi | Workflow'un bir video kaydetme düğümü olduğundan emin olun; `output/` klasörüne bakın. |

İstek sunucuya ulaştıktan sonra CLI zaman aşımı yaşarsa işlem ComfyUI üzerinde devam edebilir; aynı işi tekrar sıraya almadan `/history` durumunu kontrol edin.
