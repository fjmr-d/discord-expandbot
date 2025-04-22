import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

# -------- Flaskを使ったHealth Check対応 (Koyeb対策) --------
import threading
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

def run_flask():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_flask).start()

# -------- .envからトークンを取得 --------
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# -------- Discord Botの設定 --------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot 起動完了: {bot.user}")

# -------- ツイートURL検出＆確認ボタン --------
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
            # メッセージ削除
            await interaction.message.delete()
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

# -------- Botを起動 --------
bot.run(token)
