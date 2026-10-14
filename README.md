# MultiTalk Avatar Starter 🇹🇷

**Bir referans görüntü + bir ses kaydı → konuşan avatar videosu** oluşturmak için bağımsız, Türkçe bir **başlangıç kiti**. Çok konuşmacılı senaryoların temel akışını da açıklar.

> **Önemli:** Bu repo yeni bir yapay zekâ modeli **değildir** ve kendi başına video üretmez. Video üretimi için [MeiGen-AI/MultiTalk](https://github.com/MeiGen-AI/MultiTalk) ve uygun bir GPU çalıştırma ortamı gerekir. ComfyUI entegrasyonu [kijai/ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper) üzerinden yapılır. Model ağırlıkları veya upstream kodlar bu repoda **bulunmaz**.

## Hızlı başlangıç

### 1) Kurulum olmadan dene

MultiTalk ekibinin [topluluk demosuna referans veren GitHub sayfasına](https://github.com/MeiGen-AI/MultiTalk#-community-works) bakın. Demo üçüncü taraf hizmetidir; çevrimiçi GPU erişimi, ücret, kuyruk, kullanım koşulları ve erişilebilirlik değişebilir. Ayrıntılar: [docs/ONLINE.md](docs/ONLINE.md).

### 2) Yerel ComfyUI hazırlığı

Linux/macOS için kendi ortamında ComfyUI ve WanVideoWrapper'ı klonlayan yardımcı betik:

```bash
bash scripts/setup_comfyui.sh "$HOME/multitalk-env"
```

Bu betik **GPU PyTorch sürücüsü veya model ağırlığı kurmaz**. Çalışma ortamına uygun PyTorch kurulumu, model indirme adımları ve wrapper workflow seçimi için [docs/LOCAL.md](docs/LOCAL.md) belgesini okuyun. Windows kullanıcıları için de manuel adımlar vardır.

### 3) Fotoğraf ve sesi kontrol et

```bash
python avatar_kit.py check --image /yol/portre.png --audio /yol/konusma.wav
```

### 4) Workflow'u bağla ve üret

İlgili MultiTalk örneğini ComfyUI'de açın ve **API formatında** dışa aktarın. Workflow'daki dosya yükleme düğüm kimliklerini öğrenin:

```bash
python avatar_kit.py inspect-workflow --workflow /yol/multitalk_api.json
```

Sonra yerel dosyaları ComfyUI `input/` klasörüne kopyalayıp mevcut workflow'u sıraya alın:

```bash
python avatar_kit.py queue \
  --workflow /yol/multitalk_api.json \
  --comfy-root "$HOME/multitalk-env/ComfyUI" \
  --image /yol/portre.png --audio /yol/konusma.wav \
  --image-node 12 --audio-node 14 --dry-run
```

`12` ve `14` **örnek kimliklerdir**, workflow'unuzdan gerçek ID'leri alın. Sonuç doğruysa `--dry-run` seçeneğini kaldırın ve gerekirse `--wait` ekleyin. Bu CLI sadece yerel `127.0.0.1:8188` ComfyUI API'sine istek gönderir. **CLI'nin desteklediği düğümlerde dosya alanları `image` / `audio` değilse `--image-field` / `--audio-field` girin.** Her wrapper workflow'u bu basit bağlama biçimiyle çalışmayabilir.

### Dokümanlar

- [Online deneme](docs/ONLINE.md)
- [Yerel ComfyUI kurulumu](docs/LOCAL.md)
- [Görüntü/ses hazırlama](docs/INPUTS.md)
- [Çok konuşmacılı üretim](docs/MULTIPERSON.md)
- [Sık karşılaşılan sorunlar](docs/TROUBLESHOOTING.md)
- [Lisanslar ve üçüncü taraf içerik](docs/LEGAL.md)

## Gereksinimler

- Python 3.10+ (bu repodaki CLI standart kütüphaneyle çalışır)
- [ComfyUI](https://github.com/Comfy-Org/ComfyUI), [WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper) ve MultiTalk modelinin ayrı kurulumu
- Modelin gerektirdiği VRAM'e sahip uygun GPU; düşük VRAM ayarları hız/kaliteyi etkiler
- MP3/WAV ses ve PNG/JPEG görüntü; isteğe bağlı `ffprobe` metadata gösterebilir

## Güvenlik ve sorumlu kullanım

Yalnızca izinli/size ait görüntü ve seslerle çalışın. İzin olmadan başkasının konuştuğu izlenimini yaratacak yanıltıcı içerik üretmeyin. Gerçekçi sentetik içeriği gerektiğinde açıkça işaretleyin. Kişisel medya ve model ağırlıkları `.gitignore` ile depo dışında tutulur; push etmeden önce `git status` ile kontrol edin.

## Lisans

Burada **özgün olarak yazılan** yardımcı kod ve dokümanlar [MIT](LICENSE) lisanslıdır. **MultiTalk, Wan2.1, ComfyUI, WanVideoWrapper ve indirilen her modelin kendi lisansı ayrı geçerlidir.** Ayrıntı: [docs/LEGAL.md](docs/LEGAL.md). Repo bunların resmî ürünü, yeniden dağıtımı veya desteklenen sürümü değildir.

> İçerik fikri, kullanıcı tarafından aktarılan ve `@burhankocabiyik` etiketi bulunan konuşan avatar başlangıç kiti konusundan alınmıştır. Metinler ve CLI bağımsız olarak oluşturulmuştur; kaynak kılavuz aynen yayımlanmamıştır.

## GitHub'da yeni herkese açık depo açma

[GitHub CLI](https://cli.github.com/) kurup giriş yaptıktan sonra (`gh auth login`), bu dizinde:

```bash
bash scripts/publish_github.sh multitalk-avatar-starter
```

Betik yalnızca **yeni** herkese açık depo oluşturur, tüm yerel dosyaları `main` dalına push eder; aynı isimde depo zaten varsa veya burada `.git` varsa üzerine yazmadan çıkar. GitHub hesabınıza giriş yapmanız gerekir.
