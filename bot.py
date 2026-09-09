import discord
from discord.ext import commands
import asyncio
import os
import json
from aiohttp import web
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Discord IDs
CHARACTER_CHANNEL_ID = 1540753599020408872
PING_ROLE_ID = 1540866902451036230

# Словарь для красивого перевода названий зон из игры
ZONE_NAMES = {
    "StoneBridge": "🧭 1. Stone Bridge (Zone One)",
    "HiddenCave": "🧭 2. Hidden Cave (Zone Two)",
    "Convergence": "🧭 3. Convergence (Zone Three)"
}

class ZoneGuideView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="Watch Video Guide", 
            style=discord.ButtonStyle.link, 
            url="https://youtube.com",
            emoji="🌿"
        ))

# Функция, которая будет отправлять сообщение, когда прилетает сигнал из Roblox
async def send_zone_alert(data):
    await bot.wait_until_ready()
    channel = bot.get_channel(CHARACTER_CHANNEL_ID)
    if not channel:
        print("Ошибка: Канал не найден.")
        return

    raw_zone = data.get("zoneId", "Unknown")
    multiplier = data.get("qiMultiplier", 1)
    
    # Красиво форматируем имя зоны
    pretty_zone_name = ZONE_NAMES.get(raw_zone, f"🧭 Unknown Zone ({raw_zone})")

    ping_text = f"<@&{PING_ROLE_ID}>\n⚠️ **Attention Cultivators! A new Qi Zone has spawned directly from active servers!**"
    
    spawn_embed = discord.Embed(
        title="🟢 GLOBAL ZONE SPAWNED! 🟢",
        description=f"The active safe zone has shifted! Go there immediately to collect your bonuses.\n\n*Click the button below — the video guide will open directly inside Discord!*",
        color=discord.Color.green()
    )
    spawn_embed.add_field(name="📍 Active Location", value=f"**{pretty_zone_name}**", inline=False)
    spawn_embed.add_field(name="✨ Qi Multiplier Boost", value=f"**`x{multiplier} Qi`**", inline=False)
    spawn_embed.set_footer(text="Check this spot immediately! The zone will rotate dynamically.")
    
    await channel.send(content=ping_text, embed=spawn_embed, view=ZoneGuideView())
    print(f"Уведомление о зоне {raw_zone} успешно отправлено!")

# --- ВЕБ-СЕРВЕР ДЛЯ ПРИЕМА ВЕБХУКОВ ИЗ ROBLOX ---
async def handle_roblox_webhook(request):
    try:
        data = await request.json()
        print(f"Получены данные от Roblox: {data}")
        
        # Запускаем отправку сообщения в Дискорд в фоновом режиме бота
        bot.loop.create_task(send_zone_alert(data))
        
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"Ошибка вебхука: {e}")
        return web.Response(text="Error", status=400)

async def start_web_server():
    app = web.Application()
    app.router.add_post('/webhook', handle_roblox_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер приёма сигналов Roblox запущен на порту {port}")

@bot.event
async def on_ready():
    bot.add_view(ZoneGuideView())
    print(f"Бот {bot.user} успешно запущен как умный радар!")
    # Запускаем веб-сервер прямо внутри процесса бота
    await start_web_server()

bot.run(os.environ.get("DISCORD_TOKEN"))
