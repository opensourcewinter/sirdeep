import asyncio
import os
import shutil
import sys
from urllib.parse import urlparse

import discord

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ALLOWED_PROTOCOLS = {"http", "https"}

def validate_stream_url(url: str) -> bool:
    """Ensure stream URL is safe and uses HTTP/HTTPS to prevent SSRF and local file disclosures."""
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() in ALLOWED_PROTOCOLS and bool(parsed.netloc)
    except Exception:
        return False

def get_ffmpeg_path() -> str:
    """Finds FFmpeg dynamically without hardcoding local usernames or machine paths."""
    # 1. Custom override via environment variable
    env_path = os.getenv("FFMPEG_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Check system PATH (standard across Linux, macOS, and Windows)
    system_path = shutil.which("ffmpeg")
    if system_path:
        return system_path

    # 3. Dynamic Windows WinGet lookup using environment variables (no hardcoded usernames)
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            winget_root = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
            if os.path.exists(winget_root):
                for root, _, files in os.walk(winget_root):
                    if "ffmpeg.exe" in files:
                        return os.path.join(root, "ffmpeg.exe")

    return "ffmpeg"

class RadioPlayer:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.voice_client = None
        self.current_channel = None
        self.current_station = config.default_station
        self.is_playing = False
        self._manual_stop = False
        self.ffmpeg_executable = get_ffmpeg_path()

    async def connect_and_play(self, voice_channel: discord.VoiceChannel, station_key: str = None) -> bool:
        if station_key and station_key in self.config.stations:
            self.current_station = station_key

        try:
            if self.voice_client and self.voice_client.is_connected():
                if self.voice_client.channel.id != voice_channel.id:
                    await self.voice_client.move_to(voice_channel)
            else:
                self.voice_client = await voice_channel.connect()

            self.current_channel = voice_channel
            self.is_playing = True
            self._manual_stop = False

            # Wait for DAVE E2EE handshake
            for _ in range(25):
                if self.voice_client and self.voice_client._connection:
                    conn = self.voice_client._connection
                    if conn.can_encrypt:
                        break
                    if conn.dave_session:
                        try:
                            conn.dave_session.prepare_transition(0, conn.dave_protocol_version or 1)
                            conn.dave_session.execute_transition(0)
                        except Exception:
                            pass
                        if conn.can_encrypt:
                            break
                await asyncio.sleep(0.1)

            self._start_stream()
            return True
        except Exception as ex:
            print(f"[RADIO ERROR] Connect failed: {ex}")
            return False

    def _start_stream(self):
        if not self.voice_client or not self.voice_client.is_connected():
            return

        if self.voice_client.is_playing():
            self.voice_client.stop()

        station = self.config.stations.get(self.current_station)
        if not station or not validate_stream_url(station.url):
            print(f"[RADIO SECURITY ERROR] Invalid or disallowed stream URL for station '{self.current_station}'")
            return

        def after_playback(error):
            if error:
                print(f"[RADIO PLAY ERROR]: {error}")
            if self.is_playing and not self._manual_stop and self.voice_client and self.voice_client.is_connected():
                asyncio.run_coroutine_threadsafe(self._auto_reconnect(), self.client.loop)

        try:
            source = discord.FFmpegPCMAudio(station.url, executable=self.ffmpeg_executable, **FFMPEG_OPTIONS)
            transformed = discord.PCMVolumeTransformer(source, volume=0.85)
            self.voice_client.play(transformed, after=after_playback)
            print(f"[RADIO] Streaming '{station.name}' in {self.current_channel.name}")
        except Exception as ex:
            print(f"[RADIO ERROR] Stream start failed: {ex}")

    async def switch_station(self, station_key: str) -> bool:
        if station_key in self.config.stations:
            self.current_station = station_key
            if self.voice_client and self.voice_client.is_connected():
                self._start_stream()
                return True
        return False

    async def _auto_reconnect(self):
        await asyncio.sleep(3)
        if self.is_playing and not self._manual_stop and self.voice_client and self.voice_client.is_connected():
            self._start_stream()

    async def stop(self):
        self.is_playing = False
        self._manual_stop = True
        if self.voice_client:
            try:
                if self.voice_client.is_playing():
                    self.voice_client.stop()
                await self.voice_client.disconnect()
            except Exception:
                pass
            self.voice_client = None
            self.current_channel = None
