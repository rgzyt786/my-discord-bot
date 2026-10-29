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
WELCOME_CHANNEL_ID = 1522296520030949526

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")

@bot.event
async def on_member_join(member):
    # 1. AUTO ROLE
    try:
        role = discord.utils.get(member.guild.roles, name=MEMBERS_ROLE_NAME)
        if role:
            await member.add_roles(role)
    except Exception as e:
        print(f"Role error: {e}")

    # 2. WELCOME MESSAGE - EXACT LIKE YOUR PICTURE
    try:
        welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if welcome_channel:
            embed = discord.Embed(
                description=f"Hey {member.mention}! Welcome to the family 💜\n\n"
                            f"We grow together, we play together, we vibe together! ✨\n\n"
                            f"We are so excited you joined Gamer's Syndicate ☠️.\n"
                            f"This server is all about fun, games, music, and making real friends.\n\n"
                            f"🎮 Dive in:\n"
                            f"├ Play with us in VC\n"
                            f"├ Enjoy music & memes\n"
                            f"├ Chat, laugh, and grow with us\n"
                            f"└ Make memories together\n\n"
                            f"📜 Please check rules and get your roles!\n"
                            f"💬 Don't be shy — say hello in general!\n\n"
                            f"You are our {member.guild.member_count}th member — we were waiting for you, {member.mention}!\n"
                            f"Have an amazing time here! 🎉",
                color=0x9B59FF
            )
            embed.set_author(name=f"Welcome to the crew, {member.display_name}! 🎉", icon_url=member.display_avatar.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Gamer's Syndicate ☠️ • Thanks for joining")
            
            await welcome_channel.send(embed=embed)
            print(f"Welcomed {member.name}")
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
