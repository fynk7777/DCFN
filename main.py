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


# 起動時に動作する処理
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました^o^')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
    # ボットが準備完了したらタスクを開始
    check_members.start()  # この行を追加
    # bakabonnpapa に DM を送信
    await send_update_message()

@bot.event
async def on_message(message):
    global channel_pairs, user_word_counts, respond_words
    if message.author == bot.user:
        return

    # BUMP通知機能
    if message.author.id == 302050872383242240:
        embeds = message.embeds
        if embeds is not None and len(embeds) != 0:
            if "表示順をアップしたよ" in (embeds[0].description or ""):
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

async def send_update_message():
    update_id =  71884248932155473
    user_id = 1212687868603007067  # bakabonnpapa のユーザーID を設定する
    user = await bot.fetch_user(user_id)
    update = await bot.fetch_channel(update_id)
    await user.send("アップデートしました!!")
    await update.send("アップデートしました!!")
    for i in range(3600):
        user_id2 = 1068681860038799500
        user2 = await bot.fetch_user(user_id2)
        await user2.send("起きろ")
        await asyncio.sleep(50)

# BOTの実行
try:
    keep_alive()  # Webサーバーの起動
    bot.run(TOKEN)  # BOTの実行
except Exception as e:
    print(f'エラーが発生しました: {e}')
