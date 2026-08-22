import discord
from discord.ext import commands, tasks
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 3 ИГРОВЫЕ ЛОКАЦИИ ИЗ ВАШЕГО СКРИНШОТА
LOCATIONS = [
    {"name": "Convergence (Alpha)", "compass": "245° W", "req": "Golden Core"},
    {"name": "Convergence (Bravo)", "compass": "115° E", "req": "Golden Core"},
    {"name": "Hidden Cave", "compass": "310° NW", "req": "Golden Core"}
]

@tasks.loop(seconds=1)
async def zone_manager():
    # ⚠️ ВСТАВЬТЕ СЮДА ВАШ ID ТЕКСТОВОГО КАНАЛА ДИСКОРДА
    CHANNEL_ID = 1234567890123456789 
    channel = bot.get_channel(CHANNEL_ID)
    
    if not channel:
        return

    while True:
        # 1. Случайный выбор одной из 3-х точек
        current_zone = random.choice(LOCATIONS)
        
        # 2. Карточка о появлении зоны (Зеленая полоска, как ваша зона в игре)
        spawn_embed = discord.Embed(
            title="🟢 NEW ZONE SPAWNED! 🟢",
            description=f"A new safe zone has appeared at the location: **{current_zone['name']}**",
            color=discord.Color.green()
        )
        spawn_embed.add_field(name="🧭 Compass Heading", value=f"`{current_zone['compass']}`", inline=True)
        spawn_embed.add_field(name="🛡️ Requirement", value=f"`{current_zone['req']}+`", inline=True)
        spawn_embed.set_footer(text="This zone will disappear in exactly 80 minutes!")
        
        await channel.send(embed=spawn_embed)
        
        # 3. Таймер удержания зоны (80 минут * 60 секунд = 4800 секунд)
        await asyncio.sleep(4800)
        
        # 4. Карточка об исчезновении зоны (Красная полоска)
        despawn_embed = discord.Embed(
            title="🔴 ZONE COLLAPSED 🔴",
            description=f"The safe zone at **{current_zone['name']}** has closed. Preparing for the next shift...",
            color=discord.Color.red()
        )
        await channel.send(embed=despawn_embed)
        
        # Пауза в 5 секунд перед моментальным спавном новой зоны
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is successfully running the Roblox Zone Manager!")
    zone_manager.start()

# ⚠️ ВСТАВЬТЕ СЮДА ВАШ СЕКРЕТНЫЙ ТОКЕН БОТА
bot.run("MTU0MDc3ODk1NzI0OTU3NzA2MA.GiHtg1.iD9-08ZeIZcd0jzjj2KLhhRTPb7pbirAoUarhM")
