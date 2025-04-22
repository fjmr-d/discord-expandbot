import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

# -------- .env からトークンを読み込む --------
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# -------- Botの初期設定 --------
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容を読むために必要

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot 起動完了: {bot.user}")

# -------- URL検出＆ボタン付き確認 --------
TWITTER_REGEX = r'https?://(?:x|twitter)\.com/([^\s]+)'

class ConfirmView(discord.ui.View):
    def __init__(self, original_urls):
        super().__init__(timeout=60)
        self.original_urls = original_urls
        self.clicked = False

    @discord.ui.button(label="展開する", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.clicked:
            new_urls = [
                url.replace("twitter.com", "vxtwitter.com").replace("x.com", "vxtwitter.com")
                for url in self.original_urls
            ]
            await interaction.response.send_message("展開リンクだよ！\n" + "\n".join(new_urls))
            self.clicked = True
            self.stop()

    @discord.ui.button(label="展開しない", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.clicked:
            await interaction.response.send_message("了解、展開しないよ～", ephemeral=True)
            self.clicked = True
            self.stop()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    matches = re.findall(TWITTER_REGEX, message.content)
    if matches:
        original_urls = re.findall(r'https?://(?:x|twitter)\.com/[^\s]+', message.content)
        view = ConfirmView(original_urls)
        await message.channel.send(
            f"{message.author.mention} このツイート展開する？", view=view
        )

    await bot.process_commands(message)

# -------- Bot起動 --------
bot.run(token)
