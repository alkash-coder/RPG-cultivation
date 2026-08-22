import discord
from discord.ext import commands, tasks
import random
import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Переменная для ID канала
CHANNEL_ID = 1540753599020408872

LOCATIONS = [
    {"name": "Convergence (Alpha)", "compass": "245° W", "req": "Golden Core"},
    {"name": "Convergence (Bravo)", "compass": "115° E", "req": "Golden Core"},
    {"name": "Hidden Cave", "compass": "310° NW", "req": "Golden Core"}
]

@tasks.loop(seconds=1)
async def zone_manager():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    
    if not channel:
        print("Ошибка: Не удалось найти канал. Проверьте ID.")
        return

    while True:
        current_zone = random.choice(LOCATIONS)
        
        spawn_embed = discord.Embed(
            title="🟢 NEW ZONE SPAWNED! 🟢",
            description=f"A new safe zone has appeared at the location: **{current_zone['name']}**",
            color=discord.Color.green()
        )
        spawn_embed.add_field(name="🧭 Compass Heading", value=f"`{current_zone['compass']}`", inline=True)
        spawn_embed.add_field(name="🛡️ Requirement", value=f"`{current_zone['req']}+`", inline=True)
        spawn_embed.set_footer(text="This zone will disappear in exactly 80 minutes!")
        
        await channel.send(embed=spawn_embed)
        print(f"Зона отправлена: {current_zone['name']}")
        
        # Таймер зоны (4800 секунд = 80 минут)
        await asyncio.sleep(4800)
        
        despawn_embed = discord.Embed(
            title="🔴 ZONE COLLAPSED 🔴",
            description=f"The safe zone at **{current_zone['name']}** has closed. Preparing for the next shift...",
            color=discord.Color.red()
        )
        await channel.send(embed=despawn_embed)
        
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is successfully running the Roblox Zone Manager!")
    if not zone_manager.is_running():
        zone_manager.start()

# --- МИНИ ВЕБ-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Фиктивный веб-сервер запущен на порту {port}")
    server.serve_forever()

# Запускаем веб-сервер в отдельном потоке, чтобы он не мешал боту
threading.Thread(target=run_health_check, daemon=True).start()
# ----------------------------------------

bot.run(os.environ.get("DISCORD_TOKEN"))

