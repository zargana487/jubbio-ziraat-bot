import os
import random
import time
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands

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
# 1. JUBBIO API SUNUCU YÖNLENDİRMESİ
# ==========================================
# Kütüphanenin rotasını tamamen Jubbio sunucularına çeviriyoruz
discord.http.Route.BASE = "https://jubbio.com"

# Tüm izinleri (Intents) açıyoruz
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Botun komut ön ekini "/" yapıyoruz
bot = commands.Bot(command_prefix="/", intents=intents)

# ZCoin Veritabanı
banka_hesaplari = {}

def hesap_kontrol(user_id, username):
    if user_id not in banka_hesaplari:
        banka_hesaplari[user_id] = {
            "bakiye": 500,
            "son_gunluk": 0,
            "isim": username
        }

# ==========================================
# 2. BOT AÇILIŞ OLAYI
# ==========================================
@bot.event
async def on_ready():
    print("==================================================")
    print(f" 🤖 KANKA MÜJDE! {bot.user.name} BAŞARIYLA BAŞLATILDI!")
    print(" 🟢 Bot şu an Jubbio'da tamamen AKTİF ve ÇEVRİMİÇİ!")
    print("==================================================")
    await bot.change_presence(activity=discord.Game(name="/zhelp | Ziraat Mobil"))

# ==========================================
# 3. BANKACILIK KOMUTLARI
# ==========================================

# ---- /zhelp KOMUTU ----
@bot.command()
async def zhelp(ctx):
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
    await ctx.send(yardim_tablosu)

# ---- /banka KOMUTU ----
@bot.command()
async def banka(ctx):
    user_id = str(ctx.author.id)
    username = ctx.author.name
    hesap_kontrol(user_id, username)
    
    mevcut_bakiye = banka_hesaplari[user_id]["bakiye"]
    await ctx.send(f" 💳 **Ziraat Mobil:** Sayın **{username}**, sanal hesabınızdaki güncel bakiye: **{mevcut_bakiye} ZCoin** 🪙")

# ---- /gunluk KOMUTU ----
@bot.command()
async def gunluk(ctx):
    user_id = str(ctx.author.id)
    username = ctx.author.name
    hesap_kontrol(user_id, username)
    
    su_an = time.time()
    son_alinma = banka_hesaplari[user_id]["son_gunluk"]
    bekleme_suresi = 86400
    
    if su_an - son_alinma < bekleme_suresi:
        kalan_saniye = int(bekleme_suresi - (su_an - son_alinma))
        saat = kalan_saniye // 3600
        dakika = (kalan_saniye % 3600) // 60
        await ctx.send(f" ⏱️ **Ziraat Mobil:** Günlük ödülünüzü zaten aldınız. Tekrar almak için **{saat} saat {dakika} dakika** bekleyin.")
        return

    rastgele_odul = random.randint(200, 500)
    banka_hesaplari[user_id]["bakiye"] += rastgele_odul
    banka_hesaplari[user_id]["son_gunluk"] = su_an
    await ctx.send(f" 🎁 **Ziraat Günlük Ödül:** Tebrikler @{username}! Sanal hesabınıza **+{rastgele_odul} ZCoin** yatırıldı! 🪙")

# ==========================================
# 4. BOTU ÇALIŞTIRMA (YENİ TOKEN ENTEGRE EDİLDİ)
# ==========================================
if __name__ == "__main__":
    # Render'da Environment Variables kısmındaki TOKEN değerini de bu yeni tokenla güncellemeyi unutma kanka!
    TOKEN = os.environ.get("TOKEN", "0e90363e9152b058b1d61381d51edaa8303486a401d1a775340a152e8c7add38")
    bot.run(TOKEN)
