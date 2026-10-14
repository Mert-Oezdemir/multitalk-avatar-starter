# ComfyUI ile yerel kurulum

Bu belge MultiTalk modelini **yeniden dağıtmaz**; gereken bağımsız depoların kurulmasına rehberlik eder. Aşağıdaki komutlar sürüme ve işletim sistemine göre değişebilir.

## A. Donanımı ve bağımlılıkları kontrol et

- Python, Git, FFmpeg ve uygun GPU sürücülerini yükleyin.
- NVIDIA/CUDA, AMD/ROCm veya CPU seçeneklerini [ComfyUI resmî belgelerinden](https://github.com/Comfy-Org/ComfyUI) seçin. **PyTorch sürümünü GPU'nuza göre kurun.** 14B modelin tam sürümü için yüksek VRAM gerekebilir; düşük VRAM seçenekleri wrapper sürümüne bağlıdır.
- `python -m venv .venv` kullanarak bağımlılıkları sistem Python'undan ayırın.

## B. ComfyUI ve WanVideoWrapper

Linux/macOS:

```bash
bash scripts/setup_comfyui.sh "$HOME/multitalk-env"
```

Bu komut klonlama + ComfyUI/Wrapper `requirements.txt` kurulumunu yapar; bir platforma özel PyTorch kurulumunu veya model indirmeyi garanti etmez. Windows'ta aynı Git URL'lerini clone edip sanal ortamda paket kurulumunu elle yapabilirsiniz:

```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper
```

`pip install -r ComfyUI/requirements.txt` ve `pip install -r ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/requirements.txt` komutlarını kendi sanal ortamınızda çalıştırın.

## C. Ağırlıklar ve örnek workflow

Ağırlıkları *ilgili dağıtıcıdan ayrı ayrı* indirip wrapper'ın beklediği `ComfyUI/models/` alt dizinlerine yerleştirin. İsimler/sürüm kombinasyonları değişebildiğinden **WanVideoWrapper'ın güncel README'si ve örnek workflow'u tek kaynak** kabul edin:

- MultiTalk: https://huggingface.co/MeiGen-AI/MeiGen-MultiTalk
- Wan2.1 I2V: https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P
- Ses kodlayıcı: https://huggingface.co/TencentGameMate/chinese-wav2vec2-base
- İsteğe bağlı TTS: https://huggingface.co/hexgrad/Kokoro-82M
- Wrapper örnekleri: https://github.com/kijai/ComfyUI-WanVideoWrapper/tree/main/example_workflows

**Not:** Özgün MultiTalk Python projesindeki `weights/` dizin düzeni, WanVideoWrapper'ın `models/` dizin düzeniyle aynı olmak zorunda değildir. İkisini karıştırmayın. Ağırlıkları bu GitHub deposuna commit etmeyin.

## D. Çalıştırma

```bash
cd "$HOME/multitalk-env/ComfyUI"
.venv/bin/python main.py
```

Arayüze varsayılan olarak `http://127.0.0.1:8188` adresinden ulaşılır. Wrapper'ın örnek MultiTalk `.json` workflow'unu içeri aktarın, model dosyalarını seçin. Fotoğraf/ses düğümlerini doldurun ve önce UI üzerinden test edin.

## E. CLI ile sıra yönetimi

ComfyUI'den API-format workflow dışa aktarın (gerekliyse geliştirici modu), ardından:

```bash
python avatar_kit.py inspect-workflow --workflow multitalk_api.json
python avatar_kit.py queue --workflow multitalk_api.json \
  --comfy-root "$HOME/multitalk-env/ComfyUI" \
  --image portre.jpg --audio ses.wav \
  --image-node GERCEK_ID --audio-node GERCEK_ID --wait
```

Bu yardımcı *mevcut bir API-workflow'un iki veya üç yükleme alanını değiştirir*. MultiTalk'ın tüm graph parametrelerini otomatik keşfetmez. Farklı bir yükleyici düğümündeki girişler için `--image-field` ve `--audio-field` kullanın. Sonuçlar ComfyUI `output/` altında bulunur; sadece ses/görüntü çıkışı kaydeden workflow için `Save Video` benzeri çıktı düğümü gereklidir.
