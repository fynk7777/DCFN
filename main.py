
import discord
from discord.ext import commands
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # 必要なインテントを有効化

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def on_message(message):
    global channel_pairs, user_word_counts, respond_words
    if message.author == bot.user:
        return

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

bot.run(TOKEN)

# Discordボットの起動とHTTPサーバーの起動
try:
    keep_alive()
    bot.run(TOKEN)
except Exception as e:
    print(f'エラーが発生しました: {e}')