from PIL import Image
import os

# Görsellerin bulunduğu klasör
input_dir = r"C:\Users\user\Desktop\koşma"

# Çıktı GIF yolu
output_path = r"C:\Users\user\Desktop\koşma_animasyon.gif"

# Görselleri sıralı olarak yükle
images = []
for i in range(1, 7):
    # Frame dosya yolları (frame_1.png, frame_2.png, ... varsayıyoruz)
    img_path = os.path.join(input_dir, f"frame_{i}.png")
    
    try:
        img = Image.open(img_path)
        images.append(img)
        print(f"Yüklendi: frame_{i}.png")
    except Exception as e:
        print(f"Hata: frame_{i}.png yüklenemedi - {str(e)}")

if not images:
    print("Animasyon oluşturmak için görsel bulunamadı!")
    exit()

# Animasyon ayarları
duration = 200  # Her frame arası süre (milisecond)
loop = 0        # 0 = sonsuz döngü, 1 = bir kere, 2 = iki kere, vs.

# Animasyonu oluştur ve kaydet
images[0].save(
    output_path,
    save_all=True,
    append_images=images[1:],
    duration=duration,
    loop=loop,
    optimize=True
)

print(f"Animasyon başarıyla oluşturuldu: {output_path}")
print(f"Toplam frame sayısı: {len(images)}")
print(f"Frame süresi: {duration} ms")
print(f"Döngü: {'Sonsuz' if loop == 0 else loop + ' kere'}")