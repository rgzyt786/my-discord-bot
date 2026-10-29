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
MEMBERS_ROLE_NAME = "Members"
WELCOME_CHANNEL_ID = 1522296520030949526  # Your welcome channel

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")

@bot.event
async def on_member_join(member):
    # 1. AUTO ROLE - Members role
    try:
        role = discord.utils.get(member.guild.roles, name=MEMBERS_ROLE_NAME)
        if role:
            await member.add_roles(role)
            print(f"Gave {MEMBERS_ROLE_NAME} to {member.name}")
        else:
            print(f"Role '{MEMBERS_ROLE_NAME}' not found!")
    except Exception as e:
        print(f"Role error: {e}")

    # 2. WELCOME MESSAGE - Using ID (100% reliable)
    try:
        welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if welcome_channel:
            embed = discord.Embed(description=f"Welcome {member.mention} to **{member.guild.name}**!", color=0xFF00FF)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"{member.guild.name} • Thanks for joining")
            await welcome_channel.send(content=f"Guys welcome {member.mention} 💜", embed=embed)
            print(f"Welcomed {member.name} in {welcome_channel.name}")
        else:
            print("Welcome channel ID not found!")
    except Exception as e:
        print(f"Welcome error: {e}")

@bot.event
async def on_message(message):
    if message.author.bot: 
        return
    if message.channel.id not in RESTRICTED: 
        return
    if not message.content.startswith("m!"):
        try: 
            await message.delete()
        except: 
            pass
        return
    await bot.process_commands(message)

def run_bot():
    bot.run(os.environ.get("TOKEN"))

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_flask()
