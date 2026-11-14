import re
from collections import defaultdict
from datetime import datetime, timedelta

import discord

PHISH_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:"
    r"discord(?:app)?\.(?:gift|gifts|info|club|link|trade|top|click|vip|cc|ru|xyz)|"
    r"discorcl\.|discord-nitro\.|dlscord\.|discrod\.|discorde\.|"
    r"steam(?:community|powered)?\.(?:trade|gift|link|xyz|top|cc|ru)|"
    r"grabify\.link|iplogger\.(?:org|com)|2no\.co|yip\.su"
    r")",
    re.IGNORECASE
)

ZALGO_REGEX = re.compile(r"[\u0300-\u036f\u1dc0-\u1dff\u20d0-\u20ff\ufe20-\ufe2f]{8,}")

class SecuritySentinel:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.admin_action_history = defaultdict(list)
        self.join_history = []
        self.raid_lockdown_active = False

    def check_phishing(self, content: str) -> bool:
        return bool(PHISH_REGEX.search(content))

    def check_zalgo(self, content: str) -> bool:
        return bool(ZALGO_REGEX.search(content))

    def is_privileged(self, member: discord.Member) -> bool:
        if member.id in self.config.server.owner_ids or member.id == member.guild.owner_id:
            return True
        if hasattr(member, "guild_permissions") and member.guild_permissions.administrator:
            return True
        return False

    async def register_admin_action(self, guild: discord.Guild, actor_id: int, action_type: str, limit: int = 2, window_seconds: int = 20) -> bool:
        """Tracks rapid destructive actions (mass channel/role deletion). Returns True if limit breached."""
        if actor_id in self.config.server.owner_ids or actor_id == guild.owner_id or actor_id == self.client.user.id:
            return False

        now = datetime.now()
        self.admin_action_history[actor_id].append(now)
        recent = [t for t in self.admin_action_history[actor_id] if (now - t).total_seconds() < window_seconds]
        self.admin_action_history[actor_id] = recent

        if len(recent) >= limit:
            member = guild.get_member(actor_id)
            if member:
                await self.quarantine_user(guild, member, f"Triggered Anti-Nuke limit: {len(recent)} {action_type} actions in {window_seconds}s")
            return True
        return False

    async def quarantine_user(self, guild: discord.Guild, member: discord.Member, reason: str):
        """Strips administrative roles and applies a 7-day timeout to isolate rogue accounts."""
        try:
            # Strip dangerous roles
            roles_to_remove = [r for r in member.roles if r.permissions.administrator or r.permissions.manage_guild or r.permissions.manage_channels or r.permissions.manage_roles]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason=f"Quarantine: {reason}")

            # Apply 7-day timeout
            timeout_until = discord.utils.utcnow() + timedelta(days=7)
            await member.timeout(timeout_until, reason=f"Security Isolation: {reason}")
            print(f"[SECURITY SENTINEL] Quarantined {member.name} ({member.id}): {reason}")
        except Exception as ex:
            print(f"[SECURITY SENTINEL ERROR] Failed to quarantine {member.id}: {ex}")
