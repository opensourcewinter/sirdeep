
import discord


class AuditLogger:
    def __init__(self, client, config):
        self.client = client
        self.config = config

    def get_audit_channel(self, guild: discord.Guild) -> discord.TextChannel:
        target_name = self.config.channels.audit_logs
        return discord.utils.get(guild.text_channels, name=target_name)

    def _get_target_name(self, entry: discord.AuditLogEntry) -> str:
        target = entry.target
        if hasattr(target, "name") and target.name:
            return target.name
        if hasattr(entry.changes, "before") and hasattr(entry.changes.before, "name") and entry.changes.before.name:
            return entry.changes.before.name
        if hasattr(target, "id"):
            return f"ID: {target.id}"
        return str(target)

    async def log_audit_entry(self, entry: discord.AuditLogEntry):
        guild = entry.guild
        audit_ch = self.get_audit_channel(guild)
        if not audit_ch:
            return

        # Skip routine bot self-actions
        if entry.user and entry.user.id == self.client.user.id:
            if entry.action in [
                discord.AuditLogAction.thread_create,
                discord.AuditLogAction.thread_update,
                discord.AuditLogAction.message_delete
            ]:
                return

        actor_str = f"{entry.user.mention} (`{entry.user.name}` | `{entry.user.id}`)" if entry.user else "System / Discord"
        reason_str = f"\n◈ **Reason:** {entry.reason}" if entry.reason else ""

        action_name = str(entry.action).replace("AuditLogAction.", "")
        title = f"🛡️ AUDIT: {action_name.replace('_', ' ').upper()}"
        color = 0x00D2FF
        details = []

        if entry.action == discord.AuditLogAction.kick:
            title = "👢 MEMBER KICKED"
            color = 0xE74C3C
            details.append(f"**Target:** {getattr(entry.target, 'mention', self._get_target_name(entry))}")
        elif entry.action == discord.AuditLogAction.ban:
            title = "🔨 MEMBER BANNED"
            color = 0xC0392B
            details.append(f"**Target:** {getattr(entry.target, 'mention', self._get_target_name(entry))}")
        elif entry.action == discord.AuditLogAction.unban:
            title = "🕊️ MEMBER UNBANNED"
            color = 0x2ECC71
            details.append(f"**Target:** {getattr(entry.target, 'mention', self._get_target_name(entry))}")
        elif entry.action == discord.AuditLogAction.member_update:
            title = "⏳ MEMBER UPDATED"
            color = 0xE67E22
            details.append(f"**Target:** {getattr(entry.target, 'mention', self._get_target_name(entry))}")
            if hasattr(entry.changes, "after") and hasattr(entry.changes.after, "timed_out_until"):
                if entry.changes.after.timed_out_until:
                    title = "⏳ MEMBER TIMED OUT"
                    details.append(f"**Timeout Until:** `{entry.changes.after.timed_out_until.strftime('%Y-%m-%d %H:%M UTC')}`")
                else:
                    title = "⏳ TIMEOUT REMOVED"
        elif entry.action == discord.AuditLogAction.member_role_update:
            title = "🎭 MEMBER ROLES UPDATED"
            color = 0x3498DB
            details.append(f"**Target:** {getattr(entry.target, 'mention', self._get_target_name(entry))}")
            try:
                before_roles = getattr(entry.changes.before, "roles", [])
                after_roles = getattr(entry.changes.after, "roles", [])
                if before_roles or after_roles:
                    added = set(after_roles) - set(before_roles)
                    removed = set(before_roles) - set(after_roles)
                    if added:
                        details.append(f"**Added Roles:** {', '.join([r.mention for r in added])}")
                    if removed:
                        details.append(f"**Removed Roles:** {', '.join([r.mention for r in removed])}")
            except Exception:
                pass
        elif entry.action == discord.AuditLogAction.channel_create:
            title = "📁 CHANNEL CREATED"
            color = 0x2ECC71
            details.append(f"**Channel:** {getattr(entry.target, 'mention', self._get_target_name(entry))}")
        elif entry.action == discord.AuditLogAction.channel_delete:
            title = "🗑️ CHANNEL DELETED"
            color = 0xE74C3C
            details.append(f"**Channel Name:** `#{self._get_target_name(entry)}`")
        elif entry.action == discord.AuditLogAction.role_create:
            title = "🏷️ ROLE CREATED"
            color = 0x2ECC71
            details.append(f"**Role:** {getattr(entry.target, 'mention', self._get_target_name(entry))}")
        elif entry.action == discord.AuditLogAction.role_delete:
            title = "❌ ROLE DELETED"
            color = 0xE74C3C
            details.append(f"**Role Name:** `{self._get_target_name(entry)}`")
        else:
            details.append(f"**Target:** `{self._get_target_name(entry)}`")

        details_str = "\n".join(details)
        embed = discord.Embed(
            title=title,
            description=f"◈ **Actor / Moderator:** {actor_str}\n{details_str}{reason_str}",
            color=color,
            timestamp=discord.utils.utcnow()
        )
        if entry.user and hasattr(entry.user, "display_avatar") and entry.user.display_avatar:
            embed.set_thumbnail(url=entry.user.display_avatar.url)
        embed.set_footer(text=f"{guild.name} Security Audit ✧ Action ID: {entry.id}")

        try:
            await audit_ch.send(embed=embed)
        except Exception as ex:
            print(f"[Audit Log Error]: {ex}")

    async def log_message_delete(self, message: discord.Message):
        if not message.guild or (message.author and message.author.bot):
            return
        audit_ch = self.get_audit_channel(message.guild)
        if not audit_ch or message.channel.id == audit_ch.id:
            return

        preview = message.content[:900] if message.content else "*[No text content]*"
        att_str = ("\n**Attachments:** " + ", ".join([f"`{a.filename}`" for a in message.attachments])) if message.attachments else ""

        embed = discord.Embed(
            title="🗑️ MESSAGE DELETED",
            description=(
                f"◈ **Author:** {message.author.mention} (`{message.author.name}` | `{message.author.id}`)\n"
                f"◈ **Channel:** {message.channel.mention}\n"
                f"◈ **Content:**\n> {preview.replace(chr(10), chr(10) + '> ')}"
                f"{att_str}"
            ),
            color=0xE74C3C,
            timestamp=discord.utils.utcnow()
        )
        if message.author.display_avatar:
            embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.set_footer(text=f"{message.guild.name} Audit ✧ Message ID: {message.id}")

        try:
            await audit_ch.send(embed=embed)
        except Exception as ex:
            print(f"[Message Delete Audit Error]: {ex}")

    async def log_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild or (before.author and before.author.bot) or before.content == after.content:
            return
        audit_ch = self.get_audit_channel(before.guild)
        if not audit_ch or before.channel.id == audit_ch.id:
            return

        b_text = before.content[:450] if before.content else "*[Empty]*"
        a_text = after.content[:450] if after.content else "*[Empty]*"

        embed = discord.Embed(
            title="📝 MESSAGE EDITED",
            description=(
                f"◈ **Author:** {before.author.mention} (`{before.author.name}` | `{before.author.id}`)\n"
                f"◈ **Channel:** {before.channel.mention} ┊ [Jump to Message]({after.jump_url})\n\n"
                f"**Before:**\n> {b_text.replace(chr(10), chr(10) + '> ')}\n\n"
                f"**After:**\n> {a_text.replace(chr(10), chr(10) + '> ')}"
            ),
            color=0x3498DB,
            timestamp=discord.utils.utcnow()
        )
        if before.author.display_avatar:
            embed.set_thumbnail(url=before.author.display_avatar.url)
        embed.set_footer(text=f"{before.guild.name} Audit ✧ Message ID: {after.id}")

        try:
            await audit_ch.send(embed=embed)
        except Exception as ex:
            print(f"[Message Edit Audit Error]: {ex}")
