import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ----- Flask (Health Check用) -----
import threading
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

def run_flask():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_flask).start()

# ----- Discord Bot 起動設定 -----
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot 起動完了: {bot.user}")

# ----- URL検出＆ボタン付き確認 -----
TWITTER_REGEX = r'https?://(?:x|twitter)\.com/([^\s]+)'

class ConfirmView(discord.ui.View):
    def __init__(self, original_urls):
        super().__init__(timeout=600)  # 10分タイムアウト
        self.original_urls = original_urls
        self.clicked = False
        self.message = None  # Viewにメッセージを保持

    @discord.ui.button(label="展開する", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.clicked:
            new_urls = [
                url.replace("twitter.com", "vxtwitter.com").replace("x.com", "vxtwitter.com")
                for url in self.original_urls
            ]
            await interaction.response.send_message("展開リンクだよ！\n" + "\n".join(new_urls))
            self.clicked = True
            await interaction.message.delete()
            self.stop()

    @discord.ui.button(label="展開しない", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.clicked:
            await interaction.response.send_message("了解、展開しないよ～", ephemeral=True)
            self.clicked = True
            await interaction.message.delete()
            self.stop()

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except discord.NotFound:
                pass  # 既に削除済みでも無視

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    matches = re.findall(TWITTER_REGEX, message.content)
    if matches:
        original_urls = re.findall(r'https?://(?:x|twitter)\.com/[^\s]+', message.content)
        view = ConfirmView(original_urls)
        msg = await message.channel.send(f"{message.author.mention} このツイート展開する？", view=view)
        view.message = msg  # Viewにメッセージを渡す

    await bot.process_commands(message)

# ----- Bot起動 -----
bot.run(token)
