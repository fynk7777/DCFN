import discord
import os
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands
from keep_alive import keep_alive  # keep_aliveのインポート

# TOKENの指定
TOKEN = os.getenv("DISCORD_TOKEN")

# Intentsの設定
intents = discord.Intents.all()

# Botクライアントの初期化
bot = commands.Bot(command_prefix='!', intents=intents)

# 最新のBUMPの時刻を記録する変数
latest_bump_time = None

# 起動時に動作する処理
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました^o^')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
    # bakabonnpapa に DM を送信
    await send_update_message()

@bot.event
async def on_message(message):
    global latest_bump_time
    if message.author == bot.user:
        return

    # BUMP通知機能
    if message.author.id == 302050872383242240:
        embeds = message.embeds
        if embeds is not None and len(embeds) != 0:
            if "表示順をアップしたよ" in (embeds[0].description or ""):
                latest_bump_time = datetime.now()  # 最新のBUMPの時刻を記録
                await handle_bump_notification(message)

async def handle_bump_notification(message):
    master = datetime.now() + timedelta(hours=2)
    notice_embed = discord.Embed(
        title="BUMPを検知しました",
        description=f"<t:{int(master.timestamp())}:f> 頃に通知します",
        color=0x00BFFF,
        timestamp=datetime.now()
    )
    await message.channel.send(embed=notice_embed)
    await asyncio.sleep(7200)
    notice_embed = discord.Embed(
        title="BUMPが可能です！",
        description="</bump:947088344167366698> でBUMPできます",
        color=0x00BFFF,
        timestamp=datetime.now()
    )
    await message.channel.send(embed=notice_embed)

async def find_latest_bump(channel):
    global latest_bump_time
    async for message in channel.history(limit=100):
        if message.author.id == 302050872383242240:
            embeds = message.embeds
            if embeds and "表示順をアップしたよ" in (embeds[0].description or ""):
                latest_bump_time = message.created_at
                break

@bot.tree.command(name="latest", description="最新のBUMPの状態を確認します")
async def latest_bump(interaction: discord.Interaction):
    global latest_bump_time
    channel = interaction.channel
    await find_latest_bump(channel)

    if latest_bump_time is None:
        await interaction.response.send_message("まだBUMPは検知されていません。")
        return

    now = datetime.now()
    elapsed_time = now - latest_bump_time
    if elapsed_time >= timedelta(hours=2):
        await interaction.response.send_message("BUMPが可能です！</bump:947088344167366698>")
    else:
        next_bump_time = latest_bump_time + timedelta(hours=2)
        await interaction.response.send_message(
            f"<t:{int(next_bump_time.timestamp())}:f> 頃に通知します"
        )

async def send_update_message():
    update_id =  71884248932155473
    user_id = 1212687868603007067  # bakabonnpapa のユーザーID を設定する
    user = await bot.fetch_user(user_id)
    update = await bot.fetch_channel(update_id)
    await user.send("アップデートしました!!")
    await update.send("アップデートしました!!")

# BOTの実行
try:
    keep_alive()  # Webサーバーの起動
    bot.run(TOKEN)  # BOTの実行
except Exception as e:
    print(f'エラーが発生しました: {e}')
