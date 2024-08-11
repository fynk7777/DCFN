import discord
import os
import asyncio
import re
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from keep_alive import keep_alive

# TOKENの指定
TOKEN = os.getenv("DISCORD_TOKEN")

# Intentsの設定
intents = discord.Intents.all()

# Botクライアントの初期化
bot = commands.Bot(command_prefix='!', intents=intents)

# 最新のBUMPの時刻を記録する変数
latest_bump_time = None

# BOTロールと参加者ロールの名前を定義
BOT_ROLE_NAME = "🤖BOT"
PARTICIPANT_ROLE_NAME = "😀参加者"

# 起動時に動作する処理
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました^o^')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
    check_members.start()
    await send_update_message()

# 最新のBUMPを検知するメッセージコンテキストメニュー
@bot.tree.context_menu(name="最新のBUMP")
async def latest_bump_context(interaction: discord.Interaction, message: discord.Message):
    global latest_bump_time

    # BUMPメッセージかどうかを確認
    if message.author.id == 302050872383242240:
        embeds = message.embeds
        if embeds and len(embeds) > 0:
            if "表示順をアップしたよ" in (embeds[0].description or ""):
                latest_bump_time = message.created_at  # 最新のBUMPの時刻を記録
                await handle_bump_notification(message, interaction)

# BUMP検知と通知を処理する関数
async def handle_bump_notification(message, interaction=None):
    global latest_bump_time

    if latest_bump_time:
        notification_time = latest_bump_time + timedelta(hours=2)
        notice_embed = discord.Embed(
            title="BUMPを検知しました",
            description=f"<t:{int(notification_time.timestamp())}:f> 頃に通知します",
            color=0x00BFFF,
            timestamp=datetime.now()
        )
        if interaction:
            await interaction.response.send_message(embed=notice_embed, ephemeral=True)
        await message.channel.send(embed=notice_embed)

        await asyncio.sleep(7200)  # 2時間待機

        current_time = datetime.now()
        if current_time >= notification_time:
            notice_embed = discord.Embed(
                title="BUMPが可能です！",
                description="</bump:947088344167366698> でBUMPできます",
                color=0x00BFFF,
                timestamp=current_time
            )
            await message.channel.send(embed=notice_embed)

# 起動メッセージを送信する関数
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

# 参加者ロールの管理を行うタスク
@tasks.loop(seconds=1)
async def check_members():
    for guild in bot.guilds:
        bot_role = discord.utils.get(guild.roles, name=BOT_ROLE_NAME)
        participant_role = discord.utils.get(guild.roles, name=PARTICIPANT_ROLE_NAME)
        if bot_role and participant_role:
            for member in guild.members:
                try:
                    if bot_role in member.roles and participant_role in member.roles:
                        await member.remove_roles(participant_role)
                        print(f"Removed {PARTICIPANT_ROLE_NAME} role from {member.name}")
                    elif bot_role not in member.roles and participant_role not in member.roles:
                        await member.add_roles(participant_role)
                        print(f"Added {PARTICIPANT_ROLE_NAME} role to {member.name}")
                except discord.errors.Forbidden:
                    print(f"Failed to modify role for {member.name}: Missing Permissions")
                except discord.HTTPException as e:
                    if e.status == 429:
                        print(f"Too Many Requests: {e}")
                        await asyncio.sleep(1)
                    else:
                        print(f"An error occurred: {e}")

# メッセージが送信されたときにリンクを検出する処理
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    message_link_pattern = re.compile(r'https://discord.com/channels/(\d+)/(\d+)/(\d+)')
    match = message_link_pattern.search(message.content)

    if match:
        guild_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))

        guild = bot.get_guild(guild_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    target_message = await channel.fetch_message(message_id)
                    message_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

                    embed = discord.Embed(
                        description=f"{target_message.content}\nFrom {channel.mention}",
                        color=discord.Color.blue(),
                        timestamp=target_message.created_at
                    )
                    author_avatar_url = target_message.author.display_avatar.url
                    embed.set_author(name=target_message.author.display_name, icon_url=author_avatar_url)

                    for attachment in target_message.attachments:
                        embed.set_image(url=attachment.url)

                    button = discord.ui.Button(label="メッセージ先はこちら", url=message_link)
                    view = discord.ui.View()
                    view.add_item(button)

                    await message.channel.send(embed=embed, view=view)

                except discord.NotFound:
                    await message.channel.send('メッセージが見つかりませんでした。')
                except discord.Forbidden:
                    await message.channel.send('メッセージを表示する権限がありません。')
                except discord.HTTPException as e:
                    await message.channel.send(f'メッセージの取得に失敗しました: {e}')

# BOTの実行
try:
    keep_alive()
    bot.run(TOKEN)
except Exception as e:
    print(f'エラーが発生しました: {e}')
