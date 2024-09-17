from discord import Status, app_commands
import os
import asyncio
import re
import discord
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

ALLOWED_USERS = [ 1212687868603007067 ]  # ユーザーIDを追加

# 起動時に動作する処理
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
    check_members.start()
    await send_update_message()
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=f'DCFN'))


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
    global channel_pairs, user_word_counts, respond_words
    global latest_bump_time
    if message.author == bot.user:
        return

    embeds = message.embeds
    if embeds is not None and len(embeds) != 0:
        if "表示順をアップしたよ" in (embeds[0].description or ""):
            latest_bump_time = datetime.now()  # 最新のBUMPの時刻を記録
            await handle_bump_notification(message)

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

    # 「r!test」が送信された場合に「あ」と返す
    if message.content == "b!test" or message.content == "f!test":
        await message.channel.send("GitHubで起動されています")

@bot.tree.command(name="status",description="ステータスを設定するコマンドです")
@app_commands.describe(text="ステータスを設定します")
async def text(interaction: discord.Interaction, text: str):
    if interaction.user.id in ALLOWED_USERS:
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=f'{text}'))
        await interaction.response.send_message(f'ステータスを「{text}」に設定しました。',ephemeral=True)
    else:
        await interaction.response.send_message('このコマンドを実行する権限がありません。', ephemeral=True)

# BOTの実行
try:
    keep_alive()
    bot.run(TOKEN)
except Exception as e:
    print(f'エラーが発生しました: {e}')
