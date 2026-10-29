import discord, os
from flask import Flask
from threading import Thread
from discord.ext import commands

app = Flask('')

@app.route('/')
def home():
    return "Bot LIVE 24/7"

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

MUSIC_ID_1 = 1527781595677982910
MUSIC_ID_2 = 1527788593148596435
RESTRICTED = [MUSIC_ID_1, MUSIC_ID_2]
WELCOME_NAME = "🎉-WELCOME"

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")

@bot.event
async def on_member_join(member):
    for ch in member.guild.text_channels:
        if WELCOME_NAME in ch.name:
            embed = discord.Embed(description=f"Welcome {member.mention} to **{member.guild.name}**!", color=0xFF00FF)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"{member.guild.name} • Thanks for joining")
            try:
                await ch.send(content=f"Guys welcome {member.mention} 💜", embed=embed)
            except: pass
            break

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id not in RESTRICTED: return
    if not message.content.startswith("m!"):
        try: await message.delete()
        except: pass
        return
    await bot.process_commands(message)

def run_bot():
    bot.run(os.environ.get("TOKEN"))

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_flask()