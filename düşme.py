import os
import glob
import tkinter as tk
from PIL import Image, ImageTk, ImageOps

class AnimationApp:
    def __init__(self, root, image_folder, background_path):
        self.root = root
        self.root.title("Düşme Animasyonu")
        self.root.geometry("800x600")

        # Arka plan resmini yükle
        try:
            bg_image = Image.open(background_path)
            bg_image = bg_image.resize((800, 600), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
        except Exception as e:
            print(f"Arka plan resmi yüklenemedi: {str(e)}")
            self.bg_photo = None

        # Canvas oluştur
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        # Arka planı ekle
        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # PNG görselleri yükle
        self.images = []
        self.target_size = (200, 150)
        valid_extensions = ['.png']

        for file in sorted(glob.glob(os.path.join(image_folder, "*.png"))):
            try:
                img = Image.open(file)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img = ImageOps.pad(img, self.target_size, color=(0, 0, 0, 0), method=Image.LANCZOS)
                self.images.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print(f"{file} yüklenemedi: {str(e)}")

        if not self.images:
            print("Yüklenebilir PNG bulunamadı!")
            self.root.destroy()
            return

        # Başlangıç pozisyonu
        self.start_x = 100
        self.start_y = 500
        self.current_x = self.start_x
        self.current_y = self.start_y

        # İlk görseli ekle
        self.img_item = self.canvas.create_image(
            self.current_x,
            self.current_y,
            anchor="center",
            image=self.images[0]
        )

        # Animasyon kontrolü
        self.current_frame = 0
        self.delay = 100  # milisaniye
        self.animate()

    def animate(self):
        # Bir sonraki frame'e geç
        self.current_frame = (self.current_frame + 1) % len(self.images)

        # Görselin X pozisyonunu sağa kaydır
        self.current_x += 5
        if self.current_x > 750:
            self.current_x = self.start_x  # en sağa gelince başa dön

        # Görseli güncelle
        self.canvas.itemconfig(self.img_item, image=self.images[self.current_frame])
        self.canvas.coords(self.img_item, self.current_x, self.current_y)

        # Sonraki animasyon adımını planla
        self.root.after(self.delay, self.animate)

# Ana çalışma
if __name__ == "__main__":
    image_folder = r"C:\Users\user\Desktop\düşme"
    background_image = r"C:\Users\user\Desktop\cartoon-street-94961-xxl.jpg"

    if not os.path.exists(image_folder):
        print(f"Hata: '{image_folder}' klasörü bulunamadı.")
    elif not os.path.exists(background_image):
        print(f"Hata: Arka plan resmi bulunamadı - {background_image}")
    else:
        root = tk.Tk()
        app = AnimationApp(root, image_folder, background_image)
        root.mainloop()
