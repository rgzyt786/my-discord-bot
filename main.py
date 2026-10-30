import discord, os
from flask import Flask
from threading import Thread
from discord.ext import commands
from groq import Groq

app = Flask('')

@app.route('/')
def home():
    return "Bot LIVE 24/7 - Meera is Online"

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- YOUR OLD IDS (DON'T CHANGE) ---
MUSIC_ID_1 = 1527781595677982910
MUSIC_ID_2 = 1527788593148596435
RESTRICTED = [MUSIC_ID_1, MUSIC_ID_2]
MEMBERS_ROLE_NAME = "Members"
WELCOME_CHANNEL_ID = 1522296520030949526

# --- NEW MEERA AI ID ---
MEERA_CHANNEL_ID = 1565777117608677556

# --- GROQ CLIENT ---
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user} as Meera")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Meera in her channel"))

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

    # --- 1. MUSIC CHANNEL LOGIC (YOUR OLD CODE - SAME) ---
    if message.channel.id in RESTRICTED:
        if not message.content.startswith("m!"):
            try: 
                await message.delete()
            except: 
                pass
            return
        await bot.process_commands(message)
        return

    # --- 2. MEERA AI LOGIC (ONLY IN 1565777117608677556) ---
    if message.channel.id == MEERA_CHANNEL_ID:
        # Ignore empty messages or commands
        if not message.content or message.content.startswith("!"):
            return
        
        async with message.channel.typing():
            try:
                chat = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Your name is Meera. You are NOT Over Watcher, you are Meera. You are a cute, friendly, Gen-Z girl AI for Gamer's Syndicate Discord. If anyone asks 'who are you' or 'what is your name', say you are Meera. Keep replies short, cool, friendly, under 180 words. Never say you are Over Watcher."},
                        {"role": "user", "content": message.content}
                    ]
                )
                answer = chat.choices[0].message.content
                await message.reply(answer[:1900])
            except Exception as e:
                print(f"Meera AI Error: {e}")
                await message.reply("Ayy my brain lagged 😅 ask again, I'm Meera!")
        return

    # --- 3. OTHER CHANNELS: DO NOTHING (Meera stays silent) ---
    await bot.process_commands(message)

def run_bot():
    bot.run(os.environ.get("TOKEN"))

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if _name_ == "_main_":
    Thread(target=run_bot).start()
    run_flask()
