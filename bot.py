import discord
from discord.ext import commands, tasks
import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Discord Channel ID
CHARACTER_CHANNEL_ID = 1540753599020408872

# Discord Role ID for pinging
PING_ROLE_ID = 1540866902451036230

# Interactive URL Button Component
class ZoneGuideView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="Watch Video Guide", 
            style=discord.ButtonStyle.link, 
            url="https://youtube.com",
            emoji="🌿"
        ))

@tasks.loop(seconds=1)
async def zone_manager():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHARACTER_CHANNEL_ID)
    
    if not channel:
        print("Error: Could not find the text channel. Check your ID.")
        return

    # Запоминаем текущий час при запуске бота, чтобы он не спамил сразу, 
    # а дождался именно начала следующего ровного часа
    last_sent_hour = datetime.utcnow().hour

    while True:
        now = datetime.utcnow()
        current_hour = now.hour
        current_minute = now.minute

        # Если наступила 00 минута И этот час отличается от того, в котором мы уже отправляли сообщение
        if current_minute == 0 and current_hour != last_sent_hour:
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
            print(f"Сообщение успешно отправлено в начале часа: {current_hour}:00 UTC")
            
            # Фиксируем, что для этого часа мы сообщение УЖЕ отправили
            last_sent_hour = current_hour
            
        # Проверяем время каждые 5 секунд. Это супер-точно и не пропустит 00 минут.
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    bot.add_view(ZoneGuideView())
    print(f"Bot {bot.user} is running background clock checks.")
    if not zone_manager.is_running():
        zone_manager.start()

# --- WEB SERVER BYPASS FOR RENDER COMPLIANCE ---
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
# -----------------------------------------------

bot.run(os.environ.get("DISCORD_TOKEN"))
