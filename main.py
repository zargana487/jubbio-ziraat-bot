import os
import time
import json
import requests
import websocket
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

Thread(target=run_flask).start()

# ==========================================
# 1. BOT VE JUBBIO AYARLARI
# ==========================================
TOKEN = os.environ.get("TOKEN", "0e90363e9152b058b1d61381d51edaa8303486a401d1a775340a152e8c7add38")
API_URL = "https://jubbio.com"

# ZCoin Veritabanı
banka_hesaplari = {}

def hesap_kontrol(user_id, username):
    if user_id not in banka_hesaplari:
        banka_hesaplari[user_id] = {"bakiye": 500, "isim": username}

def mesaj_gonder(channel_id, icerik):
    try:
        url = f"{API_URL}/channels/{channel_id}/messages"
        headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
        requests.post(url, json={"content": icerik}, headers=headers)
    except:
        pass

# ==========================================
# 2. KOMUT SİSTEMİ
# ==========================================
def komutlari_isle(msg_data):
    try:
        author = msg_data.get("author", {})
        if author.get("bot"): return

        user_id = str(author.get("id"))
        username = author.get("username")
        content = msg_data.get("content", "").strip()
        channel_id = msg_data.get("channel_id")

        if not content.startswith("/"): return

        hesap_kontrol(user_id, username)
        parcalar = content.split()
        komut = parcalar[0].lower()

        if komut == "/zhelp":
            mesaj_gonder(channel_id, "🪙 **Ziraat Mobil Yardım:**\n`/banka` - Bakiyenizi gösterir.\n`/zhelp` - Menüyü açar.")
        elif komut == "/banka":
            bakiye = banka_hesaplari[user_id]["bakiye"]
            mesaj_gonder(channel_id, f"💳 **Ziraat Mobil:** Sayın **{username}**, güncel bakiyeniz: **{bakiye} ZCoin** 🪙")
    except:
        pass

# ==========================================
# 3. BOTU YEŞİL YAKAN VE BAĞLAYAN CANLI SİSTEM
# ==========================================
def on_message(ws, message):
    try:
        data = json.loads(message)
        # Eğer sunucudan yeni bir mesaj olayı gelirse komutları işle
        if data.get("t") == "MESSAGE_CREATE":
            komutlari_isle(data.get("d"))
    except:
        pass

def on_open(ws):
    print("🟢 Canlı bağlantı kuruldu! Bot şu an Jubbio'da YEMYEŞİL ve AKTİF!")
    # Jubbio'ya "Ben botum, giriş yapıyorum ve aktifim" sinyali (Identify) gönderiyoruz
    payload = {
        "op": 2,
        "d": {
            "token": TOKEN,
            "capabilities": 125,
            "properties": {"os": "linux", "browser": "disco", "device": "disco"},
            "presence": {"status": "online", "since": 0, "activities": [], "afk": False}
        }
    }
    ws.send(json.dumps(payload))

    # Botun açık kalması için her 30 saniyede bir kalp atışı (Heartbeat) gönderen arka plan döngüsü
    def heartbeat():
        while True:
            time.sleep(30)
            ws.send(json.dumps({"op": 1, "d": None}))
    Thread(target=heartbeat).start()

if __name__ == "__main__":
    # Jubbio'nun Discord taklitli resmi WebSocket Gateway adresi
    ws = websocket.WebSocketApp("wss://gateway.discord.gg/?v=9&encoding=json",
                                on_open=on_open,
                                on_message=on_message)
    ws.run_forever()
