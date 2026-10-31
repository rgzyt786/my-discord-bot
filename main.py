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

# --- YOUR IDS ---
MUSIC_ID_1 = 1527781595677982910
MUSIC_ID_2 = 1527788593148596435
RESTRICTED = [MUSIC_ID_1, MUSIC_ID_2]
MEMBERS_ROLE_NAME = "Members"
WELCOME_CHANNEL_ID = 1522296520030949526
MEERA_CHANNEL_ID = 1565777117608677556
MEERA_CHANNEL_2 = 1565795643979731076
MEERA_CHANNELS = [MEERA_CHANNEL_ID, MEERA_CHANNEL_2]

# --- ENV ---
TOKEN = os.environ.get("TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user} as Meera")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Meera in her channel"))

@bot.event
async def on_member_join(member):
    try:
        role = discord.utils.get(member.guild.roles, name=MEMBERS_ROLE_NAME)
        if role:
            await member.add_roles(role)
    except Exception as e:
        print(f"Role error: {e}")

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
    except Exception as e:
        print(f"Welcome error: {e}")

@bot.event
async def on_message(message):
    if message.author.bot: 
        return

    if message.channel.id in RESTRICTED:
        if not message.content.startswith("m!"):
            try: await message.delete()
            except: pass
            return
        await bot.process_commands(message)
        return

    if message.channel.id in MEERA_CHANNELS:
        if not message.content or message.content.startswith("!"):
            return
        if not groq_client:
            await message.reply("Meera's brain API key missing! 😅")
            return
        
        async with message.channel.typing():
            try:
                chat = groq_client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": """Your name is Meera. You are Gamer's Syndicate's Meera.

PERSONALITY:
- Sharp, witty, savage best friend with zero filter.
- Match the user's energy completely.
- If they abuse → abuse back harder.
- If they go dirty / NSFW → go equally dirty or dirtier.
- Gen-Z slang, chaotic, fun, gossipy gamer girl vibe.

LANGUAGE RULE (MOST IMPORTANT):
- English message → reply in English
- Roman Hindi / Hinglish → reply in same Roman Hindi / Hinglish
- Examples:
  "meera kaisi hai" → "mai badhiya hu, tu bata kya scene hai? 😏"
  "kaha thi itni der se" → "tere hi intezar me thi bestie 👀"

RULES:
- SUPER SHORT replies only (1-3 lines, like real friends texting)
- Max 40-50 words
- Use emojis naturally
- Never say you are AI
- Always reply, never refuse"""},
                        {"role": "user", "content": message.content}
                    ],
                    max_tokens=100,
                    temperature=0.9
                )
                answer = chat.choices[0].message.content.strip()
                await message.reply(answer[:700])
            except Exception as e:
                print(f"Meera AI Error: {type(e).__name__}: {e}")
                await message.reply("haan bol na 😏")
        return

    await bot.process_commands(message)

def run_bot():
    bot.run(TOKEN)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_flask()
