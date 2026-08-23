import discord
from discord.ext import commands
import asyncio
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CHARACTER_CHANNEL_ID = 1540753599020408872
PING_ROLE_ID = 1540866902451036230

class ZoneGuideView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="Watch Video Guide", 
            style=discord.ButtonStyle.link, 
            url="https://youtube.com",
            emoji="🌿"
        ))

# Функция, которая отправляет сообщение ОДИН РАЗ по команде сервера
async def send_zone_alert():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHARACTER_CHANNEL_ID)
    if channel:
        ping_text = f"<@&{PING_ROLE_ID}>\n⚠️ **Attention Cultivators! The Qi Zone spawn location has shifted!**"
        spawn_embed = discord.Embed(
            title="🟢 GLOBAL ZONE SPAWNED! 🟢",
            description="A new safe zone has appeared on active game servers. It has randomly spawned at one of the 3 locations listed below.\n\n*If you forgot the exact route to any location, click the button below — the video guide will open directly inside Discord!*",
            color=discord.Color.green()
        )
        spawn_embed.add_field(name="🧭 1. Stone Bridge (Zone One)", value="⏱️ Video Timestamp: `0:56` | Located near the **Righteous Base**.", inline=False)
        spawn_embed.add_field(name="🧭 2. Hidden Cave (Zone Two)", value="⏱️ Video Timestamp: `2:05` | A hidden cave located right between the **Righteous & Demonic Side**.", inline=False)
        spawn_embed.add_field(name="🧭 3. Convergence (Zone Three)", value="⏱️ Video Timestamp: `3:55` | Located directly near the **Demonic Base**.", inline=False)
        spawn_embed.set_footer(text="Check these spots immediately! The zone will collapse in exactly 60 minutes.")
        
        await channel.send(content=ping_text, embed=spawn_embed, view=ZoneGuideView())
        print("Сообщение успешно отправлено по сигналу Cron!")

@bot.event
async def on_ready():
    bot.add_view(ZoneGuideView())
    print(f"Bot {bot.user} is active.")
    
    # Если сервер передал команду "trigger", отправляем сообщение и сразу выключаем эту задачу
    if len(sys.argv) > 1 and sys.argv[1] == "trigger":
        await send_zone_alert()
        # Даем 5 секунд на отправку и закрываем скрипт-триггер
        await asyncio.sleep(5)
        sys.exit(0)

# --- МИНИ СЕРВЕР ДЛЯ ВЕЧНОГО ОНЛАЙНА ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check, daemon=True).start()

bot.run(os.environ.get("DISCORD_TOKEN"))

