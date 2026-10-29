import os
from threading import Thread
from flask import Flask

# 1. ADIM: Render'ın botu uyutmaması için minik bir Web Sunucusu oluşturuyoruz
app = Flask('')

@app.route('/')
def home():
    return "Ziraat Bank Botu 7/24 Aktif!"

def run():
    # Render'ın otomatik atadığı portu veya varsayılan olarak 8080 portunu açıyoruz
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. ADIM: Web sunucusunu bot ana döngüye girmeden önce başlatıyoruz
keep_alive()

# ========================================================
# BURADAN AŞAĞISI SENİN MEVCUT PYDROID BOT KODLARIN OLACAK
# ========================================================

print("Ziraat Bank botu başarıyla başlatıldı...")

# Örnek: Senin Jubbio botunun bağlanma kodları buraya gelecek
# Örn: client.run() veya bot.start() gibi botunu çalıştıran kodlar...
