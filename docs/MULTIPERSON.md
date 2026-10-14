# Çok konuşmacılı MultiTalk

MultiTalk, **tek bir sahne referans görüntüsündeki birden fazla karakteri**, farklı ses akışlarıyla konuşturabilecek şekilde tasarlanmıştır. Mutlaka kişi başına ayrı portre gerekmez; kişiler tek referans karede bulunabilir.

1. Her konuşmacının görüntüdeki yüzünün anlaşılır olduğundan emin olun.
2. Resmî çok konuşmacılı workflow'u kullanın; örnekte gerekli ses akışı/girişlerini inceleyin.
3. Konuşmaların zamanlamasını ses parçalarıyla eşleştirin. MultiTalk'ın farklı sürümleri/ara yüzleri konuşmacı eşlemesi için ek parametreler gerektirebilir.
4. Önce tek kişilik kısa deneme; sonra iki kişilik sahne yapın.

Bu repodaki CLI, `--audio2 ... --audio2-node ...` ekleyerek ikinci ses yükleyici düğümüne dosya yolu bağlayabilir. **Bu bayraklar tek başına çok kişili workflow üretmez:** Seçtiğiniz API-workflow'da konuşmacılar ve sahne eşleşmesi önceden doğru tanımlanmalıdır.

Örnek:

```bash
python avatar_kit.py queue --workflow two_speakers_api.json \
  --comfy-root /path/to/ComfyUI --image sahne.png --image-node 12 \
  --audio kisi1.wav --audio-node 14 --audio2 kisi2.wav --audio2-node 19 --wait
```

Buradaki ID'ler örnektir; kendi API-workflow dosyanızdakilerle değiştirin.
