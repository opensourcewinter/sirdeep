import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import discord

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from core.config import load_config
from core.security import SecuritySentinel
from core.audit import AuditLogger
from modules.radio.player import RadioPlayer
from modules.radio.view import RadioControlView
from modules.debates.engine import DebateEngine
from modules.leveling.engine import LevelingEngine
from modules.ai.engine import AIEngine
from modules.ai.view import AILoungeView

# Load environment variables
load_dotenv()

# Discord Intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.moderation = True

class SirDeepBot(discord.Client):
    def __init__(self, config):
        super().__init__(intents=intents)
        self.config = config
        self.security = SecuritySentinel(self, config)
        self.audit = AuditLogger(self, config)
        self.radio = RadioPlayer(self, config)
        self.debates = DebateEngine(self, config)
        self.leveling = LevelingEngine(self, config)
        self.ai_engine = AIEngine(config)

    async def setup_hook(self):
        # Persistent Views for 24/7 button clicks
        self.radio_view = RadioControlView(self.radio, self.config)
        self.ai_view = AILoungeView(self.leveling, self.radio_view)
        self.add_view(self.radio_view)
        self.add_view(self.ai_view)
        print("  ✓ Registered all persistent views (Radio Controller & AI Lounge)")

    async def on_ready(self):
        print("==================================================")
        print(f"  SirDeep Community Suite Online!")
        print(f"  - Logged in as: {self.user.name} ({self.user.id})")
        print(f"  - Target Guild ID: {self.config.server.guild_id}")
        print(f"  - Active Features: {', '.join([k for k, v in vars(self.config.features).items() if v])}")
        print("==================================================")
        asyncio.create_task(self.debate_scheduler_loop())

    async def debate_scheduler_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                history = self.debates._load_history()
                if history.get("last_date") != today:
                    for guild in self.guilds:
                        if guild.id == self.config.server.guild_id or self.config.server.guild_id == 0:
                            await self.debates.post_debate(guild)
            except Exception as ex:
                print(f"[DEBATE SCHEDULER ERROR]: {ex}")
            await asyncio.sleep(1800)

bot_config = load_config()
bot = SirDeepBot(bot_config)

# --- Audit Gateway Listeners ---

@bot.event
async def on_audit_log_entry_create(entry):
    if bot_config.features.audit_logging:
        await bot.audit.log_audit_entry(entry)

@bot.event
async def on_message_delete(message):
    if bot_config.features.audit_logging:
        await bot.audit.log_message_delete(message)

@bot.event
async def on_message_edit(before, after):
    if bot_config.features.audit_logging:
        await bot.audit.log_message_edit(before, after)

# --- Anti-Nuke Watchdog Listeners ---

@bot.event
async def on_guild_channel_delete(channel):
    if bot_config.features.anti_nuke:
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            await bot.security.register_admin_action(channel.guild, entry.user.id, "channel_delete", limit=2, window_seconds=20)
            break

@bot.event
async def on_guild_role_delete(role):
    if bot_config.features.anti_nuke:
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            await bot.security.register_admin_action(role.guild, entry.user.id, "role_delete", limit=2, window_seconds=20)
            break

# --- Message & Command Processing ---

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.strip()
    cmd_lower = content.lower()
    first_token = cmd_lower.split()[0] if cmd_lower else ""

    # Security Link & Zalgo Scanning
    if bot_config.features.anti_nuke and not bot.security.is_privileged(message.author):
        if bot.security.check_phishing(content):
            try:
                await message.delete()
                await message.channel.send(f"🚨 {message.author.mention} malicious link removed.", delete_after=5)
            except Exception:
                pass
            return

    # 1. Leveling & Contributor XP
    if bot_config.features.contributor_xp:
        await bot.leveling.process_message_xp(message)

    # 2. Contributor Rank / Profile Command
    if first_token in ["!rank", "!profile", "!rep"]:
        if len(message.mentions) > 0 and first_token in ["!rep", "+rep"]:
            # Granting peer rep
            target = message.mentions[0]
            reason = " ".join(content.split()[2:]) if len(content.split()) > 2 else ""
            res = await bot.leveling.award_rep(message.author, target, reason)
            await message.reply(res)
            return
        else:
            target = message.mentions[0] if message.mentions else message.author
            async with message.channel.typing():
                file = await bot.leveling.get_contributor_card_file(target, message.guild)
                await message.reply(file=file)
            return

    # 3. Radio Commands
    if first_token in ["!radio", "!lofi", "!synthwave", "!ambient", "!stop"]:
        if first_token == "!stop":
            await bot.radio.stop()
            await message.reply("⏹️ Radio stopped.")
            return

        station_key = "lofi"
        if first_token in ["!synthwave", "!ambient"]:
            station_key = first_token.replace("!", "")

        vc = message.author.voice.channel if message.author.voice else None
        if not vc:
            await message.reply(embed=discord.Embed(title="📻 Radio Controller", description="Select a station below:", color=0x00D2FF), view=bot.radio_view)
            return

        success = await bot.radio.connect_and_play(vc, station_key)
        st = bot_config.stations.get(station_key)
        if success:
            await message.reply(f"📻 Streaming **{st.emoji} {st.name}** in {vc.mention}!")
        return

    # 4. Manual Dev Debate Trigger
    if first_token in ["!debate", "!devdebate"]:
        msg = await bot.debates.post_debate(message.guild, message.channel)
        if msg:
            await message.reply(f"✅ Posted Dev Debate! Check {msg.jump_url}")
        return

    # 5. AI Chat Mention or Lounge
    is_lounge = bot_config.channels.ai_lounge in message.channel.name
    is_mentioned = bot.user in message.mentions
    if (is_lounge or is_mentioned) and not content.startswith(("!", ".", "?", "/")):
        clean_text = content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        async with message.channel.typing():
            reply = await bot.ai_engine.generate_reply(message.author.id, clean_text, message.author.display_name, message.guild.name)
            await message.reply(reply)

if __name__ == "__main__":
    token = bot_config.bot_token or os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN is missing. Set it in .env or environment variables.")
        sys.exit(1)
    bot.run(token)
