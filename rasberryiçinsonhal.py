
import paramiko
import time
import concurrent.futures
import os
import re
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# Tüm Zero'ların IP ve kimlik bilgileri
ZERO_DEVICES = {
    "Zero1": {"ip": "192.168.1.22", "user": "pico", "password": "1234"},
    "Zero2": {"ip": "192.168.1.108", "user": "pico", "password": "1234"},
    "Zero3": {"ip": "192.168.1.109", "user": "pico", "password": "1234"}
}

class ScoreWindow(QMainWindow):
    def __init__(self, scores):
        super().__init__()
        self.scores = scores
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Raspberry Pi Zero Skor Tablosu")
        self.setGeometry(100, 100, 500, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Başlık
        title = QLabel("SKOR TABLOSU")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Skor tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Cihaz", "Skor"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Kapat butonu
        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.scores))
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=                                                                                                                                                             True)
        for row, (device, score) in enumerate(sorted_scores):
            self.table.setItem(row, 0, QTableWidgetItem(device))
            self.table.setItem(row, 1, QTableWidgetItem(str(score)))

            # Yüksek skoru vurgula
            if score == max(self.scores.values()) and score > 0:
                for col in range(2):
                    self.table.item(row, col).setBackground(QColor(255, 255, 0))

def execute_ssh_command(device_info, command, timeout=15):
    """SSH ile komut çalıştır"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            device_info["ip"],
            username=device_info["user"],
            password=device_info["password"],
            timeout=timeout
        )

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        if "setlocale: LC_ALL: cannot change locale" in error:
            error = re.sub(r"bash: warning: setlocale: LC_ALL: cannot change loc                                                                                                                                                             ale.*\n?", "", error).strip()

        return output, error

    except Exception as e:
        return "", f"SSH Hatası: {str(e)}"

def start_all_devices_simultaneously():
    """Tüm cihazlara aynı anda başlama komutu gönder - bazıları başarısız olsa b                                                                                                                                                             ile devam et"""
    print("Tüm cihazlara aynı anda başlama komutu gönderiliyor...")

    def start_single_device(device_name, device_info):
        try:
            execute_ssh_command(device_info, "pkill -f anim5.py")
            time.sleep(1)
            execute_ssh_command(device_info, "echo '0' > /home/pico/score.txt")
            execute_ssh_command(device_info, "echo '' > /home/pico/anim5.log 2>/                                                                                                                                                             dev/null || true")

            output, error = execute_ssh_command(device_info,
                "cd /home/pico && python3 anim5.py > /home/pico/anim5.log 2>&1 &                                                                                                                                                             ")

            if error and "exit status" not in error and not error.startswith("ba                                                                                                                                                             sh: warning:"):
                print(f"{device_name} başlatma hatası: {error}")
                return False, device_name
            else:
                print(f"{device_name} başlatıldı")
                return True, device_name
        except Exception as e:
            print(f"{device_name} istisnası: {str(e)}")
            return False, device_name

    # Paralel başlatma
    successful_starts = []
    failed_starts = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ZERO_DEVICES)) as                                                                                                                                                              executor:
        futures = {executor.submit(start_single_device, name, info): name for na                                                                                                                                                             me, info in ZERO_DEVICES.items()}
        for future in concurrent.futures.as_completed(futures):
            success, device_name = future.result()
            if success:
                successful_starts.append(device_name)
            else:
                failed_starts.append(device_name)

    # Sonuçları raporla
    if successful_starts:
        print(f"Başarıyla başlatılan cihazlar: {', '.join(successful_starts)}")
    if failed_starts:
        print(f"Başlatılamayan cihazlar: {', '.join(failed_starts)}")

    return len(successful_starts) > 0  # En az bir cihaz başlatıldıysa True dönd                                                                                                                                                             ür

def collect_scores():
    """Tüm cihazlardan skorları topla"""
    print("Skorlar toplanıyor...")
    collected_scores = {}

    for device_name, device_info in ZERO_DEVICES.items():
        try:
            output, error = execute_ssh_command(device_info, "cat /home/pico/sco                                                                                                                                                             re.txt 2>/dev/null || echo '0'", timeout=20)
            clean_output = re.sub(r"[^0-9]", "", output)
            score = int(clean_output) if clean_output else 0
            collected_scores[device_name] = score
            print(f"{device_name} skoru: {score}")
        except Exception as e:
            print(f"{device_name} skor toplama hatası: {str(e)}")
            collected_scores[device_name] = 0

    return collected_scores

def show_scores_gui(scores):
    """Skorları PyQt5 GUI ile göster"""
    app = QApplication(sys.argv)
    window = ScoreWindow(scores)
    window.show()
    app.exec_()

def stop_all_animations():
    """Tüm cihazlardaki animasyonları durdur"""
    print("Tüm cihazlardaki oyunlar durduruluyor...")
    for device_name, device_info in ZERO_DEVICES.items():
        output, error = execute_ssh_command(device_info, "pkill -f anim5.py && s                                                                                                                                                             leep 1")
        if error and "no process found" not in error.lower():
            print(f"{device_name} durdurma hatası: {error}")
        else:
            print(f"{device_name} durduruldu")

def show_menu():
    """Terminal menüsünü göster - sadece çıkış seçeneğiyle kapanır"""
    while True:
        print("\n" + "="*50)
        print("RASPBERRY PI ZERO KONTROL MERKEZİ")
        print("="*50)
        print("1. Oyunu Başlat")
        print("2. Skorları Göster")
        print("3. Çıkış")
        print("="*50)

        try:
            choice = input("Seçiminiz (1-3): ").strip()

            if choice == "1":
                success = start_all_devices_simultaneously()
                if success:
                    print("Oyun başlatıldı! Oyun bitince 'Skorları Göster' seçen                                                                                                                                                             eğini kullanın.")
                else:
                    print("Hiçbir cihaz başlatılamadı. Lütfen bağlantıları kontr                                                                                                                                                             ol edin.")

            elif choice == "2":
                scores = collect_scores()
                if any(score > 0 for score in scores.values()):
                    show_scores_gui(scores)
                else:
                    print("Henüz skor bulunamadı veya tüm skorlar 0!")

            elif choice == "3":
                stop_all_animations()
                print("Çıkış yapılıyor...")
                break

            else:
                print("Geçersiz seçim! Lütfen 1-3 arasında bir sayı girin.")

        except KeyboardInterrupt:
            print("\n\nKullanıcı tarafından iptal edildi. Menüye dönülüyor...")
            continue
        except Exception as e:
            print(f"Bir hata oluştu: {str(e)}")
            print("Lütfen tekrar deneyin.")
            continue

def main():
    """Ana fonksiyon"""
    print("Çoklu Raspberry Pi Zero Kontrol Sistemine Hoş Geldiniz!")

    # SSH anahtar doğrulama sorununu çöz
    os.system("mkdir -p ~/.ssh && touch ~/.ssh/known_hosts")

    # Menüyü göster
    show_menu()

if __name__ == "__main__":
    main()



