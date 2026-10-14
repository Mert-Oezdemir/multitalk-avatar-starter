# Girdilerin hazırlanması

## Fotoğraf

- Rızalı, net ve tercihen önden çekilmiş bir yüz tercih edin.
- Dengeli aydınlatma ve sınırlı yüz kapanması dudak eşleşmesini kolaylaştırır.
- `.png`, `.jpg` ve `.jpeg` kabul edilir.

## Ses

- `.wav` veya `.mp3`; arka plan gürültüsü ve yankısı düşük kayıtlar kullanın.
- Çok uzun dosyalar belleği ve işleme süresini artırabilir. Başlangıç için birkaç saniyelik kısa kayıtla test edin.
- Örnek ffmpeg dönüştürme komutu (örnektir, model/workflow'un gerçek örnekleme hızını kontrol edin):

```bash
ffmpeg -i ses.mp3 -ac 1 -ar 16000 ses_mono.wav
```

## Yerel denetim

```bash
python avatar_kit.py check --image portre.png --audio ses.wav
```

CLI uzantı ve dosya imzasını doğrular; isteğe bağlı kurulu `ffprobe` ses süresini raporlayabilir. Yüz netliğini, rızayı, medya lisansını ya da tüm codec uyumluluğunu otomatik doğrulamaz.
