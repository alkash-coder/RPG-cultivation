import discord
from discord.ext import commands, tasks
import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Твой ID канала в Дискорде
CHARACTER_CHANNEL_ID = 1540753599020408872

# ID роли для пинга (уже встроен в код)
PING_ROLE_ID = 1540866902451036230

# Класс для интерактивной URL-кнопки под сообщением
class ZoneGuideView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Кнопка работает вечно, без таймаута
        # Добавляем кнопку-ссылку, которая открывает плеер YouTube прямо в Discord
        self.add_item(discord.ui.Button(
            label="Смотреть видео-гайд", 
            style=discord.ButtonStyle.link, 
            url="https://youtube.com",
            emoji="🌿"
        ))

@tasks.loop(seconds=1)
async def zone_manager():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHARACTER_CHANNEL_ID)
    
    if not channel:
        print("Ошибка: Не удалось найти текстовый канал. Проверьте ID.")
        return

    while True:
        # Текст уведомления с пингом роли над карточкой
        ping_text = f"<@&{PING_ROLE_ID}>\n⚠️ **Внимание, культиваторы! Место спавна Qi-зоны изменилось!**"
        
        # Карточка оповещения о спавне зоны (Зеленая полоска)
        spawn_embed = discord.Embed(
            title="🟢 GLOBAL ZONE SPAWNED! 🟢",
            description="Attention Cultivators! A new safe zone has appeared on active game servers. It has randomly spawned at one of the 3 locations below.\n\n*Если вы забыли точный маршрут к локациям, нажмите на кнопку под этим сообщением — видеогид откроется прямо в интерфейсе Discord!*",
            color=discord.Color.green()
        )
        spawn_embed.add_field(
            name="🧭 1. Stone Bridge (Первая зона)", 
            value="⏱️ Таймкод: `0:56` | Находится недалеко от базы праведников (**Righteous Base**).", 
            inline=False
        )
        spawn_embed.add_field(
            name="🧭 2. Hidden Cave (Вторая зона)", 
            value="⏱️ Таймкод: `2:05` | Скрытая пещера, расположена между фракциями (**Righteous & Demonic Side**).", 
            inline=False
        )
        spawn_embed.add_field(
            name="🧭 3. Convergence (Третья зона)", 
            value="⏱️ Таймкод: `3:55` | Находится прямо возле базы демонов (**Demonic Base**).", 
            inline=False
        )
        spawn_embed.set_footer(text="Check these spots immediately! The zone will collapse in exactly 80 minutes.")
        
        # Отправляем сообщение: пинг роли + эмбед + интерактивная кнопка-ссылка
        await channel.send(content=ping_text, embed=spawn_embed, view=ZoneGuideView())
        print("Автономное уведомление с кнопкой-ссылкой успешно отправлено!")
        
        # Таймер зоны (80 минут = 4800 секунд)
        await asyncio.sleep(4800)
        
        # Карточка закрытия зоны (Красная полоска)
        despawn_embed = discord.Embed(
            title="🔴 ZONE COLLAPSED 🔴",
            description="The active safe zone has closed and disappeared. Calculating the next breakthrough shift...",
            color=discord.Color.red()
        )
        await channel.send(embed=despawn_embed)
        print("Уведомление о закрытии зоны отправлено.")
        
        # Короткая пауза перед повторным запуском цикла (5 секунд)
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    # Регистрируем кнопку в памяти бота при перезапуске
    bot.add_view(ZoneGuideView())
    print(f"Bot {bot.user} is successfully running the Interactive Roblox Zone Manager!")
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

