import os
import discord
from discord.ext import commands
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
# 1. JUBBIO/DISCORD BOT AYARLARI
# ==========================================
# Tüm izinleri (Intents) açıyoruz ki mesajları okuyabilsin
intents = discord.Intents.default()
intents.message_content = True

# Botun komut ön ekini (Prefix) "/" yapıyoruz
bot = commands.Bot(command_prefix="/", intents=intents)

# ZCoin Veritabanı
banka_hesaplari = {}

def hesap_kontrol(user_id, username):
    if user_id not in banka_hesaplari:
        banka_hesaplari[user_id] = {
            "bakiye": 500,
            "isim": username
        }

# ==========================================
# 2. BOT AÇILIŞ OLAYI (BOTU YEŞİL YAKAN KISIM)
# ==========================================
@bot.event
async def on_ready():
    print(f"🤖 Kanka müjde! {bot.user.name} başarıyla Jubbio'ya bağlandı!")
    print("🟢 Bot şu an tamamen ÇEVRİMİÇİ ve aktif!")
    # Botun durum yazısını ayarlıyoruz
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
    await ctx.send(f"💳 **Ziraat Mobil:** Sayın **{username}**, sanal hesabınızdaki güncel bakiye: **{mevcut_bakiye} ZCoin** 🪙")

# ==========================================
# 4. BOTU ÇALIŞTIRMA
# ==========================================
if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN", "0e90363e9152b058b1d61381d51edaa8303486a401d1a775340a152e8c7add38")
    bot.run(TOKEN)
