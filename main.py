import os
import time
import random
import json
import requests
from threading import Thread
from flask import Flask

# ==========================================
# 0. RENDER 7/24 AKTİF TUTMA SUNUCUSU (FLASK)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Met Ziraat Botu 7/24 Aktif!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Web sunucusunu arka planda başlatıyoruz
Thread(target=run_flask).start()

# ==========================================
# 1. BOT VE JUBBIO AYARLARI
# ==========================================
# Render panelindeki Environment'a eklediğin TOKEN'ı okur
BOT_TOKEN = os.environ.get("TOKEN", "0e90363e9152b058b1d61381d51edaa8303486a401d1a775340a152e8c7add38")
API_URL = "https://jubbio.com"

KURUCU_ID = "27767" 
admin_listesi = [KURUCU_ID]

# ZCoin Veritabanı
banka_hesaplari = {}

def hesap_kontrol(user_id, username):
    if user_id not in banka_hesaplari:
        banka_hesaplari[user_id] = {
            "bakiye": 500,
            "son_gunluk": 0,
            "isim": username
        }

def mesaj_gonder(channel_id, icerik):
    try:
        url = f"{API_URL}/channels/{channel_id}/messages"
        # ÇOK KRİTİK: Token'ın başına 'Bot ' takısı ekledik, Jubbio bunu istiyor!
        headers = {
            "Authorization": f"Bot {BOT_TOKEN}", 
            "Content-Type": "application/json"
        }
        payload = {"content": icerik}
        requests.post(url, json=payload, headers=headers)
    except:
        pass

# ==========================================
# 2. KOMUT İŞLEYİCİSİ (HATASIZ TEMİZ SÜRÜM)
# ==========================================
def komutlari_isle(msg_data):
    try:
        author = msg_data.get("author", {})
        if author.get("bot"):
            return

        user_id = str(author.get("id"))
        username = author.get("username")
        content = msg_data.get("content", "").strip()
        channel_id = msg_data.get("channel_id")

        if not content.startswith("/"):
            return

        hesap_kontrol(user_id, username)
        parcalar = content.split()
        if not parcalar:
            return
            
        komut = parcalar[0].lower()

        # ---- /zhelp KOMUTU ----
        if komut == "/zhelp":
            yardim_tablosu = (
                "```\n"
                "==================== ZİRAAT BOT YARDIM MENÜSÜ ====================\n"
                "Komut       | Kullanım Formatı           | Açıklama\n"
                "------------|----------------------------|------------------------\n"
                "/zhelp      | /zhelp                     | Tüm komutları listeler.\n"
                "/banka      | /banka                     | Mevcut bakiyenizi gösterir.\n"
                "/gunluk     | /gunluk                    | 24 saatte bir günlük ödül verir.\n"
                "==================================================================\n"
                "```"
            )
            mesaj_gonder(channel_id, yardim_tablosu)

        # ---- /banka KOMUTU ----
        elif komut == "/banka":
            mevcut_bakiye = banka_hesaplari[user_id]["bakiye"]
            mesaj_gonder(channel_id, f"💳 **Ziraat Mobil:** Sayın **{username}**, sanal hesabınızdaki güncel bakiye: **{mevcut_bakiye} ZCoin** 🪙")

        # ---- /gunluk KOMUTU ----
        elif komut == "/gunluk":
            su_an = time.time()
            son_alinma = banka_hesaplari[user_id]["son_gunluk"]
            bekleme_suresi = 86400
            
            if su_an - son_alinma < bekleme_suresi:
                kalan_saniye = int(bekleme_suresi - (su_an - son_alinma))
                saat = kalan_saniye // 3600
                dakika = (kalan_saniye % 3600) // 60
                saniye = kalan_saniye % 60
                mesaj_gonder(channel_id, f"⏱️ **Ziraat Mobil:** Günlük ödülünüzu zaten aldınız. Tekrar almak için **{saat} saat {dakika} dakika** bekleyin.")
                return

            rastgele_odul = random.randint(200, 500)
            banka_hesaplari[user_id]["bakiye"] += rastgele_odul
            banka_hesaplari[user_id]["son_gunluk"] = su_an
            mesaj_gonder(channel_id, f"🎁 **Ziraat Günlük Ödül:** Tebrikler @{username}! Sanal hesabınıza **+{rastgele_odul} ZCoin** yatırıldı! 🪙")

    except Exception as e:
        print(f"Hata: {e}")

# ==========================================
# 3. KESİNTİSİZ HTTP DÖNGÜ SİSTEMİ
# ==========================================
def bot_dongusu():
    son_mesaj_id = None
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    print("🤖 Ziraat Bankası Ekonomi Botu Başlatıldı!")
    print("📡 Jubbio ağ geçidi aktif, komutlar bekleniyor...")
    
    while True:
        try:
            # Jubbio API üzerinden en yeni mesajı sürekli kontrol ediyoruz
            response = requests.get(f"{API_URL}/users/@me/messages?limit=1", headers=headers, timeout=5)
            if response.status_code == 200:
                mesajlar = response.json()
                if mesajlar and isinstance(mesajlar, list):
                    en_yeni_mesaj = mesajlar[0]
                    msg_id = en_yeni_mesaj.get("id")
                    if msg_id != son_mesaj_id:
                        son_mesaj_id = msg_id
                        komutlari_isle(en_yeni_mesaj)
        except:
            pass
        time.sleep(0.5)

if __name__ == "__main__":
    bot_dongusu()
