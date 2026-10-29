import time
import random
import json
import requests
import os
from threading import Thread
from flask import Flask

# ==========================================
# 0. RENDER 7/24 AKTİF TUTMA SUNUCUSU (FLASK)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Ziraat Bankası Botu 7/24 Aktif!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# ==========================================
# 1. BOT AYARLARI VE VERİTABANI
# ==========================================
# Render'daki TOKEN'ı çekiyoruz, yoksa koddakini kullanır
BOT_TOKEN = os.environ.get("TOKEN", "27d738ca9cb36dd04a692dee55ae25a27d81761d9c07ef54e7c83e0008a89d63")
API_URL = "https://gateway.jubbio.com/api/v1"

KURUCU_ID = "27767" 
admin_listesi = [KURUCU_ID]

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
        headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}
        payload = {"content": icerik}
        res = requests.post(url, json=payload, headers=headers)
    except:
        pass

# ==========================================
# 2. KOMUT İŞLEYİCİSİ (HATALAR DÜZELTİLDİ)
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
                "/zar        | /zar <miktar> <2-4>        | Zar çarkıyla katlama oyunu.\n"
                "/secim      | /secim <miktar> <renk>     | Siyah/Kırmızı renk kumarı.\n"
                "/adminver   | /adminver <kullanıcı_id>   | [Kurucu] Birine adminlik verir.\n"
                "/ekle       | /ekle <miktar>             | [Admin] Hesaplara para basar.\n"
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
                mesaj_gonder(channel_id, f"⏱️ **Ziraat Mobil:** Günlük ödülünüzü zaten aldınız. Tekrar almak için **{saat} saat {dakika} dakika** bekleyin.")
                return

            rastgele_odul = random.randint(200, 500)
            banka_hesaplari[user_id]["bakiye"] += rastgele_odul
            banka_hesaplari[user_id]["son_gunluk"] = su_an
            mesaj_gonder(channel_id, f"🎁 **Ziraat Günlük Ödül:** Tebrikler @{username}! Sanal hesabınıza **+{rastgele_odul} ZCoin** yatırıldı! 🪙")

        # ---- /zar KOMUTU ----
        elif komut == "/zar":
            if len(parcalar) < 3:
                mesaj_gonder(channel_id, "⚠️ Kullanım: `/zar <bahis_miktarı> <2-4 arası sayı>`")
                return
            try:
                bahis = int(parcalar[1])
                secilen_zar = int(parcalar[2])
            except:
                return
            if secilen_zar < 2 or secilen_zar > 4:
                return
            if banka_hesaplari[user_id]["bakiye"] < bahis or bahis <= 0:
                mesaj_gonder(channel_id, "❌ Yetersiz bakiye!")
                return
            
            gelen_zar = random.randint(2, 4)
            if secilen_zar == gelen_zar:
                kazanc = bahis * secilen_zar
                banka_hesaplari[user_id]["bakiye"] += (kazanc - bahis)
                mesaj_gonder(channel_id, f"🎲 Zar: **{gelen_zar}** çıktı! 🎉 **{secilen_zar}x** katı kazandın! Yeni Bakiye: **{banka_hesaplari[user_id]['bakiye']} ZCoin**")
            else:
                banka_hesaplari[user_id]["bakiye"] -= bahis
                mesaj_gonder(channel_id, f"🎲 Zar: **{gelen_zar}** çıktı! ❌ Kaybettin. Yeni Bakiye: **{banka_hesaplari[user_id]['bakiye']} ZCoin**")

        # ---- /secim KOMUTU ----
        elif komut == "/secim":
            if len(parcalar) < 3:
                return
            try:
                bahis = int(parcalar[1])
                secilen_renk = parcalar[2].lower()
            except:
                return
            if secilen_renk not in ["siyah", "kırmızı", "kirmizi"]:
                return
            if banka_hesaplari[user_id]["bakiye"] < bahis or bahis <= 0:
                mesaj_gonder(channel_id, "❌ Yetersiz bakiye!")
                return
            
            gelen_renk = random.choice(["siyah", "kırmızı"])
            if secilen_renk == "kirmizi": secilen_renk = "kırmızı"
            if secilen_renk == gelen_renk:
                banka_hesaplari[user_id]["bakiye"] += bahis
                mesaj_gonder(channel_id, f"🔴⚫ Çark: **{gelen_renk.upper()}** geldi! 🎉 Kazandın! Yeni Bakiye: **{banka_hesaplari[user_id]['bakiye']} ZCoin**")
            else:
                banka_hesaplari[user_id]["bakiye"] -= bahis
                mesaj_gonder(channel_id, f"🔴⚫ Çark: **{gelen_renk.upper()}** geldi! ❌ Kaybettin. Yeni Bakiye: **{banka_hesaplari[user_id]['bakiye']} ZCoin**")

        # ---- /adminver KOMUTU ----
        elif komut == "/adminver":
            if user_id != KURUCU_ID or len(parcalar) < 2:
                return
            hedef_id = str(parcalar[1])
            if hedef_id not in admin_listesi:
                admin_listesi.append(hedef_id)
                mesaj_gonder(channel_id, f"👑 **[SİSTEM]** `{hedef_id}` başarıyla admin yapıldı!")

        # ---- /ekle KOMUTU ----
        elif komut == "/ekle":
            if user_id not in admin_listesi or len(parcalar) < 2:
                return
            try:
                eklenecek_para = int(parcalar[1])
                banka_hesaplari[user_id]["bakiye"] += eklenecek_para
                mesaj_gonder(channel_id, f"💰 **[SİSTEM]** Hesaba **{eklenecek_para} ZCoin** eklendi! Güncel: **{banka_hesaplari[user_id]['bakiye']} ZCoin**")
            except:
                pass

    except Exception as e:
        print(f"Hata: {e}")

# ==========================================
# 3. KESİNTİSİZ DÖNGÜ SİSTEMİ
# ==========================================
def bot_dongusu():
    son_mesaj_id = None
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    print("🤖 Ziraat Bankası Ekonomi Botu Başlatıldı!")
    
    while True:
        try:
            # Jubbio API üzerinden botun kendi kanal mesajlarını dinleme endpointi
            response = requests.get(f"{API_URL}/users/@me/messages?limit=1", headers=headers, timeout=5)
            if response.status_code == 200:
                mesajlar = response.json()
                if mesajlar and isinstance(mesajlar, list):
                    en_yeni_mesaj = mesajlar[0]
                    msg_id = en_yeni_mesaj.get("id")
                    if msg_id != son_mesaj_id:
                        son_mesaj_id = msg_id
                        komutlari_isle(en_yeni_mesaj)
        except Exception as e:
            pass
        time.sleep(0.5)

if __name__ == "__main__":
    bot_dongusu()
