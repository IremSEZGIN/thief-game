import os
import glob
import tkinter as tk
from PIL import Image, ImageTk, ImageOps

class AnimationApp:
    def __init__(self, root, image_folder, background_path):
        self.root = root
        self.root.title("Fotoğraf Animasyonu")
        self.root.geometry("800x600")  # Pencere boyutu

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

        # Animasyon karelerini yükle
        self.image_folder = image_folder
        self.image_files = sorted(glob.glob(os.path.join(image_folder, "*.*")))
        self.images = []  # PhotoImage nesnelerini tutacak

        self.target_size = (200, 150)
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

        for file in self.image_files:
            if os.path.splitext(file)[1].lower() in valid_extensions:
                try:
                    img = Image.open(file)
                    # Şeffaflık koruma için RGBA formatına çevir
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    # Şeffaf dolgulu pad
                    img = ImageOps.pad(img, self.target_size, color=(0, 0, 0, 0), method=Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.images.append(photo)
                except Exception as e:
                    print(f"Hata: {file} yüklenemedi: {str(e)}")

        if not self.images:
            print("Yüklenebilir resim bulunamadı!")
            self.root.destroy()
            return

        # Animasyon başlangıç pozisyonu
        self.start_x = 100
        self.start_y = 500
        self.current_x = self.start_x
        self.current_y = self.start_y

        # İlk kareyi oluştur
        self.img_item = self.canvas.create_image(
            self.current_x,
            self.current_y,
            anchor="center",
            image=self.images[0]
        )

        # Animasyonu başlat
        self.current_frame = 0
        self.delay = 100  # ms
        self.animate()

    def animate(self):
        # Bir sonraki kareye geç
        self.current_frame = (self.current_frame + 1) % len(self.images)

        # X pozisyonunu güncelle (sağa hareket)
        self.current_x += 5

        # Ekranın sağına ulaştıysa başa dön
        if self.current_x > 750:
            self.current_x = self.start_x

        # Görseli ve pozisyonu güncelle
        self.canvas.itemconfig(self.img_item, image=self.images[self.current_frame])
        self.canvas.coords(self.img_item, self.current_x, self.current_y)

        # Sonraki kareyi planla
        self.root.after(self.delay, self.animate)

# Kullanım
if __name__ == "__main__":
    image_folder = r"C:\Users\user\Desktop\koşma"
    background_image = r"C:\Users\user\Desktop\cartoon-street-94961-xxl.jpg"

    if not os.path.exists(image_folder):
        print(f"Hata: Animasyon klasörü bulunamadı - {image_folder}")
    elif not os.path.exists(background_image):
        print(f"Hata: Arka plan resmi bulunamadı - {background_image}")
    else:
        root = tk.Tk()
        app = AnimationApp(root, image_folder, background_image)
        root.mainloop()
