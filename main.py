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

# メッセージコンテキストメニューを追加
@bot.tree.context_menu(name="最新のBUMP")
async def latest_bump_context(interaction: discord.Interaction, message: discord.Message):
    global latest_bump_time

    # BUMPメッセージかどうかを確認
    if message.author.id == 302050872383242240:
        embeds = message.embeds
        if embeds is not None and len(embeds) != 0:
            if "表示順をアップしたよ" in (embeds[0].description or ""):
                latest_bump_time = datetime.now()  # 最新のBUMPの時刻を記録
                await handle_bump_notification(message, interaction)

async def handle_bump_notification(message, interaction=None):
    master = datetime.now() + timedelta(hours=2)
    notice_embed = discord.Embed(
        title="BUMPを検知しました",
        description=f"<t:{int(master.timestamp())}:f> 頃に通知します",
        color=0x00BFFF,
        timestamp=datetime.now()
    )
    if interaction:
        await interaction.response.send_message(embed=notice_embed, ephemeral=True)  # ユーザーに一時的にメッセージを送信
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
    update_id = 1271884248932155473
    user_id = 1212687868603007067  # bakabonnpapa のユーザーID を設定する
    user = await bot.fetch_user(user_id)

    # 埋め込みメッセージの作成
    embed = discord.Embed(
        title="BOTが起動しました！",
        description="BOT has been started!",
        color=0x00BFFF,
        timestamp=datetime.now()
    )

    try:
        update = await bot.fetch_channel(update_id)
        await update.send(embed=embed)
    except discord.errors.NotFound:
        print(f"Error: Channel with ID {update_id} was not found.")

    await user.send(embed=embed)



# BOTの実行
try:
    keep_alive()  # Webサーバーの起動
    bot.run(TOKEN)  # BOTの実行
except Exception as e:
    print(f'エラーが発生しました: {e}')
