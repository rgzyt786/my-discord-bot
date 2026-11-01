import discord, os, requests
from flask import Flask
from threading import Thread
from discord.ext import commands, tasks
from groq import Groq
from datetime import datetime, timezone
from collections import defaultdict

app = Flask('')
@app.route('/')
def home():
    return "Bot LIVE 24/7 - Meera is Online"

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.moderation = True

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
FREE_GAMES_CHANNEL_ID = 1566079090648293396
VC_LOG_CHANNEL_ID = 1522299798575910985      # VC related logs
OTHER_LOG_CHANNEL_ID = 1566410101571719258   # Everything else

# --- ENV ---
TOKEN = os.environ.get("TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

announced_games = set()
conversation_history = defaultdict(list)
MAX_HISTORY = 8

async def send_vc_log(embed):
    channel = bot.get_channel(VC_LOG_CHANNEL_ID)
    if channel:
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"VC Log error: {e}")

async def send_other_log(embed):
    channel = bot.get_channel(OTHER_LOG_CHANNEL_ID)
    if channel:
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Other Log error: {e}")

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user} as Meera")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Meera in her channel"))
    
    if not check_free_games.is_running():
        check_free_games.start()

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

# ====================== VC LOGS (FIXED) ======================
@bot.event
async def on_voice_state_update(member, before, after):
    # 1. Joined VC
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(
            title="🔊 Joined Voice Channel",
            description=f"**User:** {member.mention} (`{member}`)\n**Channel:** {after.channel.mention}",
            color=0x2ecc71,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await send_vc_log(embed)
        return

    # 2. Left / Force Disconnected (Kicked from call)
    if before.channel is not None and after.channel is None:
        moderator = None
        try:
            # Discord does NOT give target for member_disconnect — only time + who did it
            async for entry in member.guild.audit_logs(limit=6, action=discord.AuditLogAction.member_disconnect):
                if (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 12:
                    moderator = entry.user
                    break
        except Exception as e:
            print(f"Audit log (disconnect) error: {e}")

        if moderator:
            embed = discord.Embed(
                title="⛔ Kicked / Force Disconnected from VC",
                description=f"**User:** {member.mention} (`{member}`)\n"
                            f"**Disconnected by:** {moderator.mention}\n"
                            f"**From:** {before.channel.mention}",
                color=0xe74c3c,
                timestamp=datetime.now(timezone.utc)
            )
        else:
            embed = discord.Embed(
                title="🔇 Left Voice Channel",
                description=f"**User:** {member.mention} (`{member}`)\n**Channel:** {before.channel.mention}",
                color=0xe74c3c,
                timestamp=datetime.now(timezone.utc)
            )
        embed.set_thumbnail(url=member.display_avatar.url)
        await send_vc_log(embed)
        return

    # 3. Moved from one VC to another
    if before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
        moderator = None
        try:
            # Discord does NOT give target for member_move either — only time + who did it
            async for entry in member.guild.audit_logs(limit=6, action=discord.AuditLogAction.member_move):
                if (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 12:
                    moderator = entry.user
                    break
        except Exception as e:
            print(f"Audit log (move) error: {e}")

        if moderator:
            embed = discord.Embed(
                title="📌 Moved / Dragged by Moderator",
                description=f"**User:** {member.mention}\n"
                            f"**Moved by:** {moderator.mention}\n"
                            f"**From:** {before.channel.mention}\n"
                            f"**To:** {after.channel.mention}",
                color=0xf39c12,
                timestamp=datetime.now(timezone.utc)
            )
        else:
            embed = discord.Embed(
                title="🔄 Moved Voice Channel",
                description=f"**User:** {member.mention}\n"
                            f"**From:** {before.channel.mention}\n"
                            f"**To:** {after.channel.mention}",
                color=0xf1c40f,
                timestamp=datetime.now(timezone.utc)
            )
        embed.set_thumbnail(url=member.display_avatar.url)
        await send_vc_log(embed)
        return

    # 4. Server Mute / Deafen
    if before.mute != after.mute or before.deaf != after.deaf:
        try:
            async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                if entry.target and entry.target.id == member.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 12:
                    changes = []
                    if before.mute != after.mute:
                        changes.append(f"Server Mute: {'Yes' if after.mute else 'No'}")
                    if before.deaf != after.deaf:
                        changes.append(f"Server Deafen: {'Yes' if after.deaf else 'No'}")
                    
                    if changes:
                        embed = discord.Embed(
                            title="🔇 Voice Mute / Deafen Updated",
                            description=f"**User:** {member.mention}\n**By:** {entry.user.mention}\n**Changes:** {', '.join(changes)}",
                            color=0x3498db,
                            timestamp=datetime.now(timezone.utc)
                        )
                        embed.set_thumbnail(url=member.display_avatar.url)
                        await send_vc_log(embed)
                    return
        except Exception as e:
            print(f"Audit log (mute/deafen) error: {e}")

# ====================== OTHER LOGS ======================
@bot.event
async def on_member_remove(member):
    # Kick
    async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
        if entry.target.id == member.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 20:
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**User:** {member.mention} (`{member}`)\n"
                            f"**Kicked by:** {entry.user.mention}\n"
                            f"**Reason:** {entry.reason or 'No reason'}",
                color=0xe67e22,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await send_other_log(embed)
            return

    # Normal Leave
    embed = discord.Embed(
        title="👋 Member Left",
        description=f"**User:** {member.mention} (`{member}`)\n"
                    f"**Account Created:** {discord.utils.format_dt(member.created_at, 'R')}",
        color=0x95a5a6,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await send_other_log(embed)

@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
        if entry.target.id == user.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 20:
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**User:** {user} (`{user.id}`)\n"
                            f"**Banned by:** {entry.user.mention}\n"
                            f"**Reason:** {entry.reason or 'No reason'}",
                color=0xc0392b,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            await send_other_log(embed)
            return

@bot.event
async def on_member_unban(guild, user):
    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.unban):
        if entry.target.id == user.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 20:
            embed = discord.Embed(
                title="♻️ Member Unbanned",
                description=f"**User:** {user} (`{user.id}`)\n"
                            f"**Unbanned by:** {entry.user.mention}",
                color=0x27ae60,
                timestamp=datetime.now(timezone.utc)
            )
            await send_other_log(embed)
            return

@bot.event
async def on_member_update(before, after):
    # Timeout
    if before.timed_out_until != after.timed_out_until and after.timed_out_until:
        async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
            if entry.target.id == after.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 20:
                embed = discord.Embed(
                    title="⏳ Member Timed Out",
                    description=f"**User:** {after.mention}\n"
                                f"**By:** {entry.user.mention}\n"
                                f"**Until:** {discord.utils.format_dt(after.timed_out_until, 'F')}\n"
                                f"**Reason:** {entry.reason or 'No reason'}",
                    color=0x9b59b6,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.set_thumbnail(url=after.display_avatar.url)
                await send_other_log(embed)
                return

    # Nickname Change
    if before.nick != after.nick:
        changer = None
        async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
            if entry.target.id == after.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 20:
                for change in entry.changes:
                    if change.key == "nick":
                        changer = entry.user
                        break
                if changer:
                    break

        desc = (f"**User:** {after.mention}\n"
                f"**Before:** `{before.nick or before.name}`\n"
                f"**After:** `{after.nick or after.name}`\n")

        if changer:
            if changer.id == after.id:
                desc += f"**Changed by:** Self"
            else:
                desc += f"**Changed by:** {changer.mention}"
        else:
            desc += f"**Changed by:** Self / Unknown"

        embed = discord.Embed(
            title="📝 Nickname Changed",
            description=desc,
            color=0x1abc9c,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        await send_other_log(embed)

    # Role Add / Remove
    if before.roles != after.roles:
        added = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]
        if added or removed:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                if entry.target.id == after.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 20:
                    desc = f"**User:** {after.mention}\n**By:** {entry.user.mention}\n"
                    if added:
                        desc += f"**Added:** {', '.join(r.mention for r in added)}\n"
                    if removed:
                        desc += f"**Removed:** {', '.join(r.mention for r in removed)}"
                    
                    embed = discord.Embed(
                        title="🎭 Roles Updated",
                        description=desc,
                        color=0x9b59b6,
                        timestamp=datetime.now(timezone.utc)
                    )
                    embed.set_thumbnail(url=after.display_avatar.url)
                    await send_other_log(embed)
                    return

# =============== FIXED MESSAGE DELETE (using raw event) ===============
@bot.event
async def on_raw_message_delete(payload):
    # This event always fires, even if message is not in cache
    if not payload.guild_id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return

    # Try to get the message from cache (if available)
    message = payload.cached_message

    author = None
    content = "No content available (message was not cached)"

    if message:
        author = message.author
        content = message.content or ""
        if not content and message.embeds:
            content = "[Embed Message]"
        if not content:
            content = "No text content"
    else:
        # Message not in cache → we can only show limited info
        content = "Message content not available (not in bot cache)"

    # Find who deleted it
    deleter = None
    try:
        async for entry in guild.audit_logs(limit=8, action=discord.AuditLogAction.message_delete):
            if entry.target and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 30:
                # When deleting someone else's message, target is the author
                if message and entry.target.id == message.author.id:
                    deleter = entry.user
                    break
                # Fallback: take the most recent message_delete action
                if not message:
                    deleter = entry.user
                    break
    except Exception as e:
        print(f"Audit log error: {e}")

    # Build description
    if author:
        author_text = f"{author.mention} (`{author}`)"
    else:
        author_text = f"Unknown (ID: {payload.cached_message.author.id if payload.cached_message else 'N/A'})"

    description = (
        f"**Author:** {author_text}\n"
        f"**Channel:** {channel.mention}\n"
        f"**Content:**\n```{content[:1000]}```\n\n"
    )

    if deleter:
        if message and deleter.id == message.author.id:
            description += f"**Deleted by:** Self"
        else:
            description += f"**Deleted by:** {deleter.mention} (`{deleter}`)"
    else:
        description += f"**Deleted by:** Unknown (No audit log found)"

    embed = discord.Embed(
        title="🗑️ Message Deleted",
        description=description,
        color=0xe74c3c,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text=f"Message ID: {payload.message_id}")

    await send_other_log(embed)

@bot.event
async def on_guild_channel_create(channel):
    creator = None
    async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_create):
        if entry.target.id == channel.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 15:
            creator = entry.user
            break

    description = (
        f"**Channel:** {channel.mention}\n"
        f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
    )
    if creator:
        description += f"**Created by:** {creator.mention}"
    else:
        description += f"**Created by:** Unknown"

    embed = discord.Embed(
        title="📁 Channel Created",
        description=description,
        color=0x2ecc71,
        timestamp=datetime.now(timezone.utc)
    )
    await send_other_log(embed)

@bot.event
async def on_guild_channel_delete(channel):
    deleter = None
    async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_delete):
        if entry.target.id == channel.id and (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 15:
            deleter = entry.user
            break

    description = (
        f"**Channel Name:** `{channel.name}`\n"
        f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
    )
    if deleter:
        description += f"**Deleted by:** {deleter.mention}"
    else:
        description += f"**Deleted by:** Unknown"

    embed = discord.Embed(
        title="📁 Channel Deleted",
        description=description,
        color=0xe74c3c,
        timestamp=datetime.now(timezone.utc)
    )
    await send_other_log(embed)

# ====================== MEERA AI ======================
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
        
        user_id = message.author.id
        user_message = message.content
        conversation_history[user_id].append({"role": "user", "content": user_message})
        if len(conversation_history[user_id]) > MAX_HISTORY:
            conversation_history[use
