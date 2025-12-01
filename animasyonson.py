
pico@pi:~ $ cat anim5.py
import pygame
import serial
import time
import os
import sys
from pygame.locals import *

import os
os.environ['DISPLAY'] = ':0'
os.environ['XAUTHORITY'] = '/home/pico/.Xauthority'

# Seri port bağlantısı
try:
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        timeout=0.1
    )
    print("Arduino bağlantısı başarılı")
except serial.SerialException as e:
    print(f"Arduino bağlantı hatası: {e}")
    ser = None

# Pygame başlat
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Top Darbesi Oyunu")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)

# Yollar
RUN_PATH = "/home/pico/koşma/"
FALL_PATH = "/home/pico/düşme/"
BG_PATH = "/home/pico/arkaplan/"

# Arkaplanı yükle
try:
    background = pygame.image.load(os.path.join(BG_PATH, "arkaplan.jpg"))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    print("Arkaplan başarıyla yüklendi")
except:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)

# Animasyon boyutları (1.5 kat büyük)
SCALE_FACTOR = 1.5
BASE_CHAR_WIDTH = WIDTH // 6
BASE_CHAR_HEIGHT = HEIGHT // 4
CHAR_WIDTH = int(BASE_CHAR_WIDTH * SCALE_FACTOR)
CHAR_HEIGHT = int(BASE_CHAR_HEIGHT * SCALE_FACTOR)

# Animasyon karelerini yükle ve tutarlı boyuta getir
def load_animation_frames(path, prefix, frame_count):
    frames = []
    for i in range(1, frame_count + 1):
        try:
            frame = pygame.image.load(os.path.join(path, f"{prefix}{i}.png"))

            # Orijinal boyutları al
            original_width, original_height = frame.get_size()

            # En boy oranını koruyarak ölçekle
            aspect_ratio = original_width / original_height
            if aspect_ratio > 1.0:  # Geniş kareler
                new_width = CHAR_WIDTH
                new_height = int(new_width / aspect_ratio)
            else:  # Dar kareler
                new_height = CHAR_HEIGHT
                new_width = int(new_height * aspect_ratio)

            # Tüm kareleri aynı hedef boyuta getir (siyah arkaplan üzerine)
            scaled_frame = pygame.Surface((CHAR_WIDTH, CHAR_HEIGHT), pygame.SRCALPHA)
            scaled_frame.fill((0, 0, 0, 0))  # Şeffaf arkaplan

            # Orantılı olarak ölçeklenmiş resmi yüzeyin ortasına yerleştir
            resized_frame = pygame.transform.scale(frame, (new_width, new_height))
            x_offset = (CHAR_WIDTH - new_width) // 2
            y_offset = (CHAR_HEIGHT - new_height) // 2
            scaled_frame.blit(resized_frame, (x_offset, y_offset))

            frames.append(scaled_frame)
        except pygame.error as e:
            print(f"Resim yükleme hatası: {e}")
            # Hata durumunda basit kare
            dummy_frame = pygame.Surface((CHAR_WIDTH, CHAR_HEIGHT))
            dummy_frame.fill(RED)
            frames.append(dummy_frame)
    return frames

# Animasyon karelerini yükle
run_frames = load_animation_frames(RUN_PATH, "frame_", 6)
fall_frames = load_animation_frames(FALL_PATH, "kare_", 5)

# Oyun değişkenleri
puan = 0
game_time = 120  # 2 dakika (saniye cinsinden)
start_time = time.time()
current_animation = "run"
current_frame = 0
last_frame_time = time.time()
run_frame_delay = 0.05  # saniye (0.1'den 0.05'e düşürüldü) - DEĞİŞTİRİLDİ
fall_frame_delay = 0.1  # saniye (düşme animasyonu için farklı gecikme)
font = pygame.font.SysFont(None, 74)
small_font = pygame.font.SysFont(None, 48)

# Hareket değişkenleri
character_x = -50  # Ekranın solundan biraz içeride başla
character_y = HEIGHT - 6  # Ekranın en altı (6 piksel üstte)
character_speed = 8  # Hareket hızı

# Oyun başlangıcında skor dosyasını sıfırla
with open("/home/pico/score.txt", "w") as f:
    f.write("0")

print("Oyun başlıyor...")

# Ana oyun döngüsü
clock = pygame.time.Clock()
running = True

def reset_character():
    """Karakteri başlangıç pozisyonuna sıfırla"""
    global character_x
    character_x = -50  # Ekranın solundan biraz içeride başla

reset_character()

while running:
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, game_time - elapsed_time)

    # Olayları işle
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
        elif event.type == KEYDOWN and event.key == K_d:  # Test için D tuşu
            current_animation = "fall"
            current_frame = 0
            last_frame_time = current_time

    # Seri porttan veri oku
    if ser and ser.in_waiting > 0:
        try:
            raw_data = ser.readline().decode('utf-8', errors='ignore').strip()
            if raw_data == "D":
                puan += 10
                current_animation = "fall"
                current_frame = 0
                last_frame_time = current_time
        except Exception as e:
            print(f"Seri okuma hatası: {e}")

    # Animasyon güncelleme
    if current_animation == "run":
        if current_time - last_frame_time > run_frame_delay:  # DEĞİŞTİRİLDİ
            current_frame = (current_frame + 1) % len(run_frames)
            last_frame_time = current_time
        # Karakteri ileri hareket ettir
        character_x += character_speed

        # Ekranın dışına çıktıysa başa al
        if character_x > WIDTH:
            character_x = -50

    elif current_animation == "fall":
        if current_time - last_frame_time > fall_frame_delay:  # DEĞİŞTİRİLDİ
            if current_frame < len(fall_frames) - 1:
                current_frame += 1
                last_frame_time = current_time
            else:
                # Son karede 3 saniye bekle
                if current_time - last_frame_time > 3.0:
                    current_animation = "run"
                    current_frame = 0
                    reset_character()

    # Ekranı temizle ve arkaplanı çiz
    screen.blit(background, (0, 0))

    # Animasyonu çiz
    if current_animation == "run":
        frame = run_frames[current_frame]
    else:
        frame = fall_frames[current_frame]

    # Karakterin pozisyonunu ayarla
    frame_rect = frame.get_rect(midbottom=(character_x + CHAR_WIDTH // 2, character_y))
    screen.blit(frame, frame_rect)

    # Puanı ve süreyi göster
    puan_text = font.render(f"Puan: {puan}", True, YELLOW)
    screen.blit(puan_text, (20, 20))

    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    time_text = font.render(f"{minutes:02d}:{seconds:02d}", True, GREEN)
    screen.blit(time_text, (WIDTH - 200, 20))

    # Oyun süresi dolduysa
    if remaining_time <= 0:
        # Skoru dosyaya yaz
        with open("/home/pico/score.txt", "w") as f:
            f.write(str(puan))

        # Ayrıca log da yaz
        with open("/home/pico/anim5.log", "a") as f:
            f.write(f"{time.time()}: Oyun bitti. Toplam Puan: {puan}\n")

        # Yarı saydam arkaplan
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        game_over_text = font.render("OYUN BİTTİ!", True, RED)
        final_score_text = font.render(f"Toplam Puan: {puan}", True, YELLOW)
        restart_text = small_font.render("Çıkmak için ESC tuşuna basın", True, GREEN)

        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))

        pygame.display.flip()

        # Çıkış için bekle
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    waiting = False
                    running = False
            clock.tick(30)

    pygame.display.flip()
    clock.tick(60)  # FPS limiti

# Temizlik
pygame.quit()
if ser:
    ser.close()
sys.exit()
