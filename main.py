import discord
import os
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# BUMP検知および通知機能
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "/bump" in message.content:  # BUMPコマンドを検知
        await handle_bump_notification(message)

    await bot.process_commands(message)

async def handle_bump_notification(message):
    master = datetime.now() + timedelta(hours=2)
    notice_embed = discord.Embed(
        title="BUMPを検知しました",
        description=f"<t:{int(master.timestamp())}:f> 頃に通知します",
        color=0x00BFFF,
        timestamp=datetime.now()
    )
    await message.channel.send(embed=notice_embed)
    await asyncio.sleep(7200)  # 2時間待機
    notice_embed = discord.Embed(
        title="BUMPが可能です！",
        description="</bump:947088344167366698> でBUMPできます",
        color=0x00BFFF,
        timestamp=datetime.now()
    )
    await message.channel.send(embed=notice_embed)

# トークンを環境変数から取得してBOTを実行
bot.run(os.getenv("DISCORD_TOKEN"))
