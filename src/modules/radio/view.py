import discord

class RadioControlView(discord.ui.View):
    def __init__(self, radio_player, config):
        super().__init__(timeout=None)
        self.radio = radio_player
        self.config = config

    @discord.ui.button(label="Lo-Fi Chill", style=discord.ButtonStyle.primary, emoji="☕", custom_id="ow_radio_lofi", row=0)
    async def btn_lofi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_station(interaction, "lofi")

    @discord.ui.button(label="Synthwave Hack", style=discord.ButtonStyle.primary, emoji="⚡", custom_id="ow_radio_synth", row=0)
    async def btn_synth(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_station(interaction, "synthwave")

    @discord.ui.button(label="Deep Focus", style=discord.ButtonStyle.primary, emoji="🌌", custom_id="ow_radio_ambient", row=0)
    async def btn_ambient(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_station(interaction, "ambient")

    @discord.ui.button(label="Connect to My VC", style=discord.ButtonStyle.success, emoji="🔊", custom_id="ow_radio_join", row=1)
    async def btn_join(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        vc = (
            (interaction.user.voice.channel if interaction.user.voice else None)
            or discord.utils.find(lambda c: "lounge" in c.name.lower() or "chill" in c.name.lower(), guild.voice_channels)
        )
        if not vc:
            await interaction.response.send_message("❌ Please join a voice channel first!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        success = await self.radio.connect_and_play(vc, self.radio.current_station)
        st = self.config.stations.get(self.radio.current_station)
        st_name = st.name if st else self.radio.current_station
        if success:
            await interaction.followup.send(f"🔊 Connected to **{vc.name}** and streaming **{st_name}**!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Failed to connect to voice channel.", ephemeral=True)

    @discord.ui.button(label="Stop / Leave", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="ow_radio_stop", row=1)
    async def btn_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.radio.voice_client and self.radio.voice_client.is_connected():
            await self.radio.stop()
            await interaction.response.send_message("⏹️ Stream stopped and disconnected from voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Radio is not currently active.", ephemeral=True)

    async def _handle_station(self, interaction: discord.Interaction, station_name: str):
        guild = interaction.guild
        st = self.config.stations.get(station_name)
        if not st:
            await interaction.response.send_message("❌ Station not found in configuration.", ephemeral=True)
            return

        if self.radio.voice_client and self.radio.voice_client.is_connected():
            await self.radio.switch_station(station_name)
            await interaction.response.send_message(f"📻 Switched to **{st.emoji} {st.name}**!", ephemeral=True)
        else:
            vc = (
                (interaction.user.voice.channel if interaction.user.voice else None)
                or discord.utils.find(lambda c: "lounge" in c.name.lower() or "chill" in c.name.lower(), guild.voice_channels)
            )
            if not vc:
                await interaction.response.send_message("❌ Please join a voice channel first!", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)
            success = await self.radio.connect_and_play(vc, station_name)
            if success:
                await interaction.followup.send(f"📻 Connected to **{vc.name}** and streaming **{st.emoji} {st.name}**!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Failed to connect to voice channel.", ephemeral=True)
