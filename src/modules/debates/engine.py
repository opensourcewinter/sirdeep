import json
import os
import random
from datetime import datetime

import discord


class DebateEngine:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.debates_file = os.path.join(base_dir, "config", "debates.json")
        self.history_file = os.path.join(base_dir, "data", "debates_history.json")
        self.debates = self._load_debates()

    def _load_debates(self):
        if os.path.exists(self.debates_file):
            try:
                with open(self.debates_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"used_indices": [], "day_count": 0, "last_date": ""}

    def _save_history(self, data):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as ex:
            print(f"[DEBATE ERROR] Failed to save history: {ex}")

    def get_next_debate(self):
        if not self.debates:
            return None

        history = self._load_history()
        used = history.get("used_indices", [])
        day = history.get("day_count", 0) + 1

        if len(used) >= len(self.debates):
            used = []

        available = [i for i in range(len(self.debates)) if i not in used]
        chosen_idx = random.choice(available)
        used.append(chosen_idx)

        history["used_indices"] = used
        history["day_count"] = day
        history["last_date"] = datetime.now().strftime("%Y-%m-%d")
        self._save_history(history)

        item = self.debates[chosen_idx]
        return {
            "day": day,
            "title": item["title"],
            "category": item["category"],
            "question": item["question"],
            "points": item.get("points", [])
        }

    async def post_debate(self, guild: discord.Guild, target_channel: discord.TextChannel = None) -> discord.Message:
        if not target_channel:
            ch_name = self.config.channels.dev_discussions
            target_channel = discord.utils.get(guild.text_channels, name=ch_name)

        if not target_channel:
            return None

        debate = self.get_next_debate()
        if not debate:
            return None

        embed = discord.Embed(
            title=f"🧠 DEV ARCHITECTURE DEBATE ┊ #{debate['day']}: {debate['title']}",
            description=(
                f"### {debate['category']}\n\n"
                f"> **\"{debate['question']}\"**\n\n"
                f"◈ **KEY ARCHITECTURAL TRADE-OFFS:**\n"
                + "\n".join([f"• {p}" for p in debate["points"]]) + "\n\n"
                "◈ **COMMUNITY GUIDELINES:**\n"
                "Jump into the **💬 Discussion Thread** attached below! Post your real-world benchmarks, war stories, and code snippets."
            ),
            color=0x00D2FF,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"{guild.name} Engineering Debates ✧ Powered by OpenWinter")

        try:
            msg = await target_channel.send(embed=embed)
            short_title = debate['title'][:38] + ("..." if len(debate['title']) > 38 else "")
            thread = await msg.create_thread(
                name=f"💬 Dev Debate #{debate['day']}: {short_title}",
                auto_archive_duration=1440
            )
            await thread.send(
                f"👋 **Welcome to Debate #{debate['day']}!**\n\n"
                f"What has been your hands-on experience with this trade-off in production? "
                f"Share your architecture diagrams, benchmarks, and favorite patterns below!"
            )
            return msg
        except Exception as ex:
            print(f"[DEBATE ERROR] Failed to post debate: {ex}")
            return None
