import json
import os
import random
from datetime import datetime

import discord

from .cards import render_contributor_card


class LevelingEngine:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.data_file = os.path.join(base_dir, "data", "reputation.json")
        self.user_xp_cooldown = {}
        self.user_rep_cooldown = {}
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as ex:
            print(f"[LEVELING ERROR] Failed to save data: {ex}")

    def get_needed_xp(self, level: int) -> int:
        return int(80 * (level ** 1.35))

    async def process_message_xp(self, message: discord.Message):
        author = message.author
        if author.bot or not message.guild:
            return

        now = datetime.now()
        last_time = self.user_xp_cooldown.get(author.id)
        if last_time and (now - last_time).total_seconds() < 45:
            return

        self.user_xp_cooldown[author.id] = now
        uid = str(author.id)
        user_record = self.data.setdefault(uid, {"xp": 0, "level": 1, "rep": 0})

        # Calculate XP: Base + Code Block Bonus + Forum/Thread Bonus
        earned = random.randint(15, 25)
        if "```" in message.content or any(domain in message.content.lower() for domain in ["github.com", "gitlab.com"]):
            earned += 15
        if isinstance(message.channel, discord.Thread):
            earned += 10

        user_record["xp"] += earned
        needed = self.get_needed_xp(user_record["level"])

        if user_record["xp"] >= needed:
            user_record["level"] += 1
            user_record["xp"] -= needed
            new_lvl = user_record["level"]
            self._save_data()

            # Milestone promotion: Level 5 -> Contributor Role
            if new_lvl >= 5:
                contrib_role = discord.utils.get(message.guild.roles, name=self.config.roles.contributor)
                if contrib_role and contrib_role not in author.roles:
                    try:
                        await author.add_roles(contrib_role, reason="Contributor Level 5 reached!")
                    except Exception:
                        pass

            tier_name = "🌱 Builder" if new_lvl < 5 else ("🛠️ Contributor" if new_lvl < 15 else "⚡ Senior Architect")
            lvl_embed = discord.Embed(
                title=f"❄️ CONTRIBUTOR LEVEL UP ┊ Level {new_lvl}!",
                description=f"Congratulations {author.mention}! Your engineering contributions have promoted you to **Level {new_lvl} ({tier_name})**.",
                color=0x00D2FF
            )
            if author.display_avatar:
                lvl_embed.set_thumbnail(url=author.display_avatar.url)
            lvl_embed.set_footer(text=f"{message.guild.name} Ecosystem ✧ Build together. Share freely.")
            await message.channel.send(embed=lvl_embed)
        else:
            self._save_data()

    async def award_rep(self, giver: discord.Member, receiver: discord.Member, reason: str = "") -> str:
        if receiver.id == giver.id:
            return "❌ You cannot award reputation points to yourself!"
        if receiver.bot:
            return "❌ Bots do not accept human reputation points."

        now = datetime.now()
        pair_key = (giver.id, receiver.id)
        last_rep = self.user_rep_cooldown.get(pair_key)
        if last_rep and (now - last_rep).total_seconds() < 43200:
            hrs = int((43200 - (now - last_rep).total_seconds()) // 3600)
            return f"⏳ You have already awarded reputation to {receiver.mention} recently. Please wait {hrs}h before awarding rep again."

        self.user_rep_cooldown[pair_key] = now
        receiver_data = self.data.setdefault(str(receiver.id), {"xp": 0, "level": 1, "rep": 0})
        receiver_data["rep"] = receiver_data.get("rep", 0) + 10
        self._save_data()

        reason_display = f"\n> *\"{reason}\"*" if reason else ""
        return (
            f"🌟 **+10 Contributor Rep** awarded to {receiver.mention}! {reason_display}\n"
            f"Total reputation score: **{receiver_data['rep']} Rep**."
        )

    async def get_contributor_card_file(self, member: discord.Member, guild: discord.Guild) -> discord.File:
        user_record = self.data.get(str(member.id), {"xp": 0, "level": 1, "rep": 0})
        lvl = user_record.get("level", 1)
        xp = user_record.get("xp", 0)
        needed = self.get_needed_xp(lvl)
        rep_pts = user_record.get("rep", 0)

        sorted_users = sorted(self.data.items(), key=lambda x: (x[1].get("level", 1), x[1].get("xp", 0)), reverse=True)
        rank_pos = 1
        for idx, (uid, _) in enumerate(sorted_users, 1):
            if uid == str(member.id):
                rank_pos = idx
                break

        specializations = []
        for r in member.roles:
            if any(k in r.name.lower() for k in ["systems", "web", "ai", "machine learning", "ui", "design", "contributor"]):
                if r.name not in specializations and not r.is_default():
                    specializations.append(r.name)

        buf = await render_contributor_card(
            member, guild, level=lvl, xp=xp, needed_xp=needed, rank_pos=rank_pos, rep_points=rep_pts, specializations=specializations
        )
        return discord.File(buf, filename="contributor_card.png")
