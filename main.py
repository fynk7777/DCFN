from discord import app_commands
import os
import asyncio
import re
import discord
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from keep_alive import keep_alive
from discord.ui import Button, View
import sys

# TOKENの指定
TOKEN = os.getenv("DISCORD_TOKEN")
start_message = os.getenv("message")

# Intentsの設定
intents = discord.Intents.all()
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # メンバー関連のイベントを有効にする

# Botクライアントの初期化
bot = commands.Bot(command_prefix='!', intents=intents)

# 最新のBUMPの時刻を記録する変数
latest_bump_time = None

# BOTロールと参加者ロールの名前を定義
BOT_ROLE_NAME = "🤖BOT"
PARTICIPANT_ROLE_NAME = "😀参加者"

ROLE_ID = 1267947998374268939  # 特定のロールID
TARGET_CHANNELS = [1272202112003997726, ]  # 特定のチャンネルIDリスト(threadのやつ)

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
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name='DCFN'))

class CloseThreadView(View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id

    @discord.ui.button(label="CLOSE", style=discord.ButtonStyle.red)
    async def close_thread(self, interaction: discord.Interaction, button: Button):
        # スレ主か指定ロールを持つ人のみが使用可能
        if interaction.user.id == self.author_id or ROLE_ID in [role.id for role in interaction.user.roles]:
            # スレッドの名前を変更
            new_name = f"【CLOSED】{interaction.channel.name}"
            embed = discord.Embed(title="CLOSEしました",description="",color=0xff0000)
            await interaction.channel.send(embed=embed)
            await interaction.channel.edit(name=new_name, archived=True)
            await interaction.channel.edit(locked=True)
        else:
            await interaction.response.send_message("この操作はできません。", ephemeral=True)

class OpenThreadView(View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id

@bot.event
async def on_thread_create(thread):
    print(f"スレッドが作成されました: {thread.name}, チャンネルID: {thread.parent_id}")
    # 指定されたチャンネルでのみ動作
    if thread.parent_id in TARGET_CHANNELS:
        async for message in thread.history(limit=1, oldest_first=True):
            creator_id = message.author.id
            creator_mention = f"<@{creator_id}>"

            role_mention = f"<@&{ROLE_ID}>"
            embed = discord.Embed(description=f"{creator_mention} さん\n運営の対応までしばらくお待ちください。", color=0x00ff00)
            view = CloseThreadView(author_id=creator_id)

            await thread.send(content=role_mention, embed=embed, view=view)
            break
    else:
        print("検知されたスレッドは指定されたチャンネルではありません。")

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
        title=f"{start_message}",
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

@bot.event
async def on_message(message):
    message_content = message.content
    message_id = message.id
    guild = message.guild
    channel = message.channel
    channel_name = channel.name
    channel_id = channel.id
    user = message.author
    user_id = user.id
    user_name = user.name
    user_avatar = user.avatar
    server_id = message.guild.id
    file = message.attachments
    file_url = file[0].url if file else None
    message_embeds = message.embeds
    

    if server_id == 1267365569678802965:
        if channel_id == 1271568627728121927:
            send_channel_id = 1299927508736540754
            send_channel = await bot.fetch_channel(send_channel_id)
            if file_url:
                await send_channel.send(file_url)

            if message.embeds:
                original_embed = message.embeds[0]  # 最初の埋め込みを取得
                await send_channel.send(embed=original_embed)
        else:
            send_channel_id = 1299912523062972507
            send_channel = await bot.fetch_channel(send_channel_id)
            target_message_link = f"https://discord.com/channels/{server_id}/{channel_id}/{message_id}"
            message_Embed = discord.Embed(
                title=f"{user_name}",
                description=f"{message_content}",
                color=0x00ff00 ,
                timestamp=datetime.now()
            )
            message_Embed.set_thumbnail(url=f"{user_avatar}")
            message_Embed.set_footer(text=f"{channel_name}")

            view = discord.ui.View(timeout=None)
            view.add_item(
                discord.ui.Button(
                    label="メッセージ先はこちら",
                    style=discord.ButtonStyle.link,
                    url=target_message_link
                )
            )

            await send_channel.send(embed=message_Embed , view=view)
            if file_url:
                await send_channel.send(file_url)

            if message.embeds:
                original_embed = message.embeds[0]  # 最初の埋め込みを取得
                await send_channel.send(embed=original_embed)

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
        server_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))

        guild = bot.get_guild(server_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    target_message = await channel.fetch_message(message_id)
                    message_link = f"https://discord.com/channels/{server_id}/{channel_id}/{message_id}"

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

    if message.content == "DCFN!bot stop":
        if server_id == 1267365569678802965:
            if user_id == 1212687868603007067:
                embed = discord.Embed(title='BOTが停止しました^^',description="起動させるにはRenderでClear Cashe & Deployをする必要があります",color=0xff0000,timestamp=datetime.utcnow())
                await message.channel.send(embed=embed)
                sys.exit()
            else:
                await message.channel.send("あなたにはこの操作を行う権限がありません。")
    # 「r!test」が送信された場合に「あ」と返す
    elif message.content == "b!test" or message.content == "DCFN!test":
        await message.channel.send("GitHubで起動されています")
    # 「r!vsc」が送信された場合にvscのリンクを返す
    elif message.content == "DCFN!vsc":
        if user_id == 1212687868603007067:
            await message.channel.send("https://vscode.dev/github/fynk7777/fortnite-server?vscode-lang=ja")
    elif message.content == "DCFN!link":
        await message.channel.send("https://github.com/fynk7777/DCFN")

    if isinstance(message.channel, discord.TextChannel) and message.channel.is_news():
        # メッセージを公開
        await message.publish()

@bot.tree.command(name="status",description="ステータスを設定するコマンドです")
@app_commands.describe(text="ステータスを設定します")
async def text(interaction: discord.Interaction, text: str):
    if interaction.user.id in ALLOWED_USERS:
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=f'{text}'))
        await interaction.response.send_message(f'ステータスを「{text}」に設定しました。',ephemeral=True)
    else:
        await interaction.response.send_message('このコマンドを実行する権限がありません。', ephemeral=True)

@bot.tree.command(name="bump_time", description="最後にbumpした時間を指定し、その2時間後に通知を送信します")
@app_commands.describe(hour="最後にbumpした時間の時", minutes="最後にbumpした時間の分")
async def bump_time(interaction: discord.Interaction, hour: int, minutes: int):
    global latest_bump_time
    now = datetime.now()
    bump_time = now.replace(hour=hour, minute=minutes, second=0, microsecond=0)
    # BUMPの時間が現在よりも過去の場合でも、2時間後の未来時間を計算する
    bump_time_with_offset = bump_time + timedelta(hours=2)
    if bump_time_with_offset < now:
        # 2時間後が過去の場合、翌日の時間として処理
        bump_time_with_offset += timedelta(days=1)
    # 2時間後の待機時間を計算
    time_diff = bump_time_with_offset - now
    minutes_diff = int(time_diff.total_seconds() // 60)
    minutes_diff = minutes_diff - 539
    total_seconds = int(time_diff.total_seconds())
    total_seconds = total_seconds - 32340
    print(total_seconds)
    await interaction.response.send_message(f"最後にBUMPした時間: {hour}:{minutes} に基づき、約{minutes_diff + 1}分後に通知を送信します。", ephemeral=True)
    await asyncio.sleep(total_seconds)
    # 通知を送信
    notice_embed = discord.Embed(
        title="BUMPが可能です！",
        description="</bump:947088344167366698> でBUMPできます",
        color=0x00BFFF,
        timestamp=datetime.now()
    )
    await interaction.channel.send(embed=notice_embed)

@bot.event
async def on_message_delete(message):
    message_content = message.content
    message_id = message.id
    channel = message.channel
    channel_name = channel.name
    channel_id = channel.id
    user = message.author
    user_name = user.name
    user_avatar = user.avatar
    server_id = message.guild.id
    file = message.attachments
    file_url = file[0].url if file else None

    if server_id == 1267365569678802965:
        send_channel_id = 1299912537063559278
        send_channel = await bot.fetch_channel(send_channel_id)
        target_message_link = f"https://discord.com/channels/{server_id}/{channel_id}/{message_id}"
        message_Embed = discord.Embed(
            title=f"{user_name}",
            description=f"{message_content}",
            color=0xff0000 ,
            timestamp=datetime.now()
        )
        message_Embed.set_thumbnail(url=f"{user_avatar}")
        message_Embed.set_footer(text=f"{channel_name}")
        
        await send_channel.send(embed=message_Embed)
        if file_url:
            await send_channel.send(file_url)
            
        if message.embeds:
            original_embed = message.embeds[0]  # 最初の埋め込みを取得
            await send_channel.send(embed=original_embed)

@bot.event
async def on_message_edit(before, after):
    before_content = before.content
    message_content = after.content
    message_id = after.id
    channel = after.channel
    channel_name = channel.name
    channel_id = channel.id
    user = after.author
    user_name = user.name
    user_avatar = user.avatar
    server_id = after.guild.id

    if server_id == 1267365569678802965:
        send_channel_id = 1299912551928430642
        send_channel = await bot.fetch_channel(send_channel_id)
        target_message_link = f"https://discord.com/channels/{server_id}/{channel_id}/{message_id}"
        message_Embed = discord.Embed(
            title=f"{user_name}",
            description=f"{before_content} \n<:down_arrow_bot:1299916586106224742><:down_arrow_bot:1299916586106224742><:down_arrow_bot:1299916586106224742><:down_arrow_bot:1299916586106224742><:down_arrow_bot:1299916586106224742>\n{message_content}",
            color=0xffff00 ,
            timestamp=datetime.now()
        )
        message_Embed.set_thumbnail(url=f"{user_avatar}")
        message_Embed.set_footer(text=f"{channel_name}")

        await send_channel.send(embed=message_Embed)

        if after.embeds:
            original_embed = after.embeds[0]  # 最初の埋め込みを取得
            await send_channel.send(embed=original_embed)

@bot.event 
async def on_member_join(member):
    user = member
    user_name = user.name
    user_avatar = user.avatar
    user_id = user.id
    create = user.created_at
    global_name = user.global_name
    server_id = user.guild.id

    if server_id == 1267365569678802965:
        send_channel_id = 1299912609209909299
        send_channel = await bot.fetch_channel(send_channel_id)
        message_Embed = discord.Embed(
            title=f"{user_name}",
            color=0x00ff00,
            description=f"name：{user_name}\nid：{user_id}\ncreated_at：{create}\nglobal_name：{global_name}",
            timestamp=datetime.now(),
        )
        message_Embed.set_thumbnail(url=f"{user_avatar}")
        await send_channel.send(embed=message_Embed)

@bot.event
async def on_raw_member_remove(member):
    user = member
    user_name = user.name
    user_avatar = user.avatar
    user_id = user.id
    create = user.created_at
    global_name = user.global_name
    server_id = user.guild.id

    if server_id == 1267365569678802965:
        send_channel_id = 1299912643516094464
        send_channel = await bot.fetch_channel(send_channel_id)
        message_Embed = discord.Embed(
            title=f"{user_name}",
            color=0xff0000,
            description=f"name：{user_name}\nid：{user_id}\ncreated_at：{create}\nglobal_name：{global_name}",
            timestamp=datetime.now(),
        )
        message_Embed.set_thumbnail(url=f"{user_avatar}")
        await send_channel.send(embed=message_Embed)

@bot.event
async def on_voice_state_update(member, before, after):
    user = member
    user_name = user.name
    user_avatar = user.avatar
    channel_id = None
    channel_name = None
    server_id = user.guild.id
    before_channel = before.channel
    after_channel = after.channel

    # 変更後のチャンネルが存在する場合のみ channel_id と channel_name を取得
    if after_channel is not None:
        channel_id = after_channel.id
        channel_name = after_channel.name
    else:
        channel_id = before_channel.id
        channel_name = before_channel.name

    if before_channel != after_channel:
        if server_id == 1267365569678802965:
            send_channel_id = 1299912657368911903
            send_channel = await bot.fetch_channel(send_channel_id)

            if before.channel is not None:
                message_Embed = discord.Embed(
                    title=f"{user_name}",
                    color=0xff0000,
                    description=f"{user_name}が<#{before_channel.id}>から退出しました",
                    timestamp=datetime.now(),
                )
                message_Embed.set_thumbnail(url=f"{user_avatar}")
                message_Embed.set_footer(text=f"{before_channel.name}")
                await send_channel.send(embed=message_Embed)

            if after.channel is not None:
                message_Embed = discord.Embed(
                    title=f"{user_name}",
                    color=0x00ff00,
                    description=f"{user_name}が<#{channel_id}>に入室しました",
                    timestamp=datetime.now(),
                )
                message_Embed.set_thumbnail(url=f"{user_avatar}")
                message_Embed.set_footer(text=f"{channel_name}")
                await send_channel.send(embed=message_Embed)


# BOTの実行
try:
    keep_alive()
    bot.run(TOKEN)
except Exception as e:
    print(f'エラーが発生しました: {e}')
