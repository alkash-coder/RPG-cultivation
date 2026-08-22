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

# Твой ID канала в Дискорде
CHARACTER_CHANNEL_ID = 1540753599020408872

@tasks.loop(seconds=1)
async def zone_manager():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHARACTER_CHANNEL_ID)
    
    if not channel:
        print("Ошибка: Не удалось найти текстовый канал. Проверьте ID.")
        return

    while True:
        # Карточка оповещения о спавне зоны (Зеленая полоска)
        spawn_embed = discord.Embed(
            title="🟢 GLOBAL ZONE SPAWNED! 🟢",
            description="Attention Cultivators! A new safe zone has appeared on active game servers. It has randomly spawned at one of the 3 locations below:",
            color=discord.Color.green()
        )
        spawn_embed.add_field(name="🧭 1. Convergence (Alpha)", value="Heading: `245° W` | Golden Core+", inline=False)
        spawn_embed.add_field(name="🧭 2. Convergence (Bravo)", value="Heading: `115° E` | Golden Core+", inline=False)
        spawn_embed.add_field(name="🧭 3. Hidden Cave", value="Heading: `310° NW` | Golden Core+", inline=False)
        spawn_embed.set_footer(text="Check these spots immediately! The zone will collapse in exactly 80 minutes.")
        
        await channel.send(embed=spawn_embed)
        print("Автономное уведомление о спавне успешно отправлено!")
        
        # Основной таймер зоны (4800 секунд = 80 минут)
        await asyncio.sleep(4800)
        
        # Карточка закрытия зоны (Красная полоска)
        despawn_embed = discord.Embed(
            title="🔴 ZONE COLLAPSED 🔴",
            description="The active safe zone has closed and disappeared. Calculating the next breakthrough shift...",
            color=discord.Color.red()
        )
        await channel.send(embed=despawn_embed)
        print("Уведомление о закрытии зоны отправлено.")
        
        # Небольшая техническая пауза перед моментальным перезапуском следующей зоны
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is successfully running the Autonomous Roblox Zone Manager!")
    if not zone_manager.is_running():
        zone_manager.start()

# --- МИНИ ВЕБ-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and bypasses render checks!")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check, daemon=True).start()
# ----------------------------------------

bot.run(os.environ.get("DISCORD_TOKEN"))
