import random
import discord

STARTERS = [
    "What open-source tech or architecture are you currently building?",
    "What is your favorite systems or web framework right now and why?",
    "If you could open-source any proprietary tool tomorrow, what would it be?",
    "What is the most stubborn bug or race condition you've squashed recently?",
    "Tabs or spaces, and what editor are you using for daily work?"
]

class AILoungeView(discord.ui.View):
    def __init__(self, leveling_engine, radio_view):
        super().__init__(timeout=None)
        self.leveling = leveling_engine
        self.radio_view = radio_view

    @discord.ui.button(label="My Contributor Profile", style=discord.ButtonStyle.primary, emoji="📊", custom_id="ow_ai_btn_profile", row=0)
    async def btn_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            file = await self.leveling.get_contributor_card_file(interaction.user, interaction.guild)
            await interaction.followup.send(file=file, ephemeral=True)
        except Exception as ex:
            await interaction.followup.send(f"❌ Failed to generate profile card: {ex}", ephemeral=True)

    @discord.ui.button(label="Coding Radio", style=discord.ButtonStyle.secondary, emoji="📻", custom_id="ow_ai_btn_radio", row=0)
    async def btn_radio(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📻 24/7 CODING RADIO & FOCUS LOUNGE",
            description=(
                "Tune in to uninterrupted background audio for programming sessions.\n\n"
                "• ☕ **24/7 Lo-Fi Chillhop** — Smooth beats for problem solving.\n"
                "• ⚡ **Nightwave Synthwave** — Cyberpunk drive for hacking.\n"
                "• 🌌 **Deep Focus Ambient** — Atmospheric soundscapes without drums.\n\n"
                "Click a station button below to tune in!"
            ),
            color=0x00D2FF
        )
        await interaction.response.send_message(embed=embed, view=self.radio_view, ephemeral=True)

    @discord.ui.button(label="Conversation Starter", style=discord.ButtonStyle.secondary, emoji="💡", custom_id="ow_ai_btn_starter", row=1)
    async def btn_starter(self, interaction: discord.Interaction, button: discord.ui.Button):
        topic = random.choice(STARTERS)
        await interaction.response.send_message(
            f"💡 **Open-Source Engineering Discussion Starter:**\n> *\"{topic}\"*\nSend your thoughts right into this channel to talk!",
            ephemeral=True
        )

    @discord.ui.button(label="Reset My Memory", style=discord.ButtonStyle.danger, emoji="🧹", custom_id="ow_ai_btn_reset", row=1)
    async def btn_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        client = interaction.client
        if hasattr(client, "ai_engine") and interaction.user.id in client.ai_engine.chat_memory:
            client.ai_engine.chat_memory[interaction.user.id].clear()
        await interaction.response.send_message("🧠✨ **Memory cleared!** Next message will start a brand new conversation.", ephemeral=True)
