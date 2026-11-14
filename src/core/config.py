import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ServerConfig:
    guild_id: int = 0
    owner_ids: List[int] = field(default_factory=list)
    name: str = "OpenWinter"
    tagline: str = "Build together. Share freely."

@dataclass
class ChannelsConfig:
    audit_logs: str = "audit-logs"
    dev_discussions: str = "dev-discussions"
    ai_lounge: str = "talk-with-sirdeep"
    watercooler: str = "watercooler"
    welcome: str = "welcome"

@dataclass
class RolesConfig:
    lead: str = "Founder / Core Lead"
    maintainer: str = "Core Maintainer"
    contributor: str = "Contributor"
    builder: str = "Builder"

@dataclass
class FeaturesConfig:
    anti_nuke: bool = True
    audit_logging: bool = True
    dev_debates: bool = True
    coding_radio: bool = True
    contributor_xp: bool = True
    ai_lounge: bool = True

@dataclass
class RadioStation:
    name: str
    url: str
    emoji: str = "📻"
    description: str = ""

@dataclass
class AIConfig:
    provider: str = "openrouter"
    model: str = "google/gemma-4-26b-a4b-it:free"
    max_memory_messages: int = 20
    memory_ttl_seconds: int = 7200

class AppConfig:
    def __init__(self, config_dict: Dict[str, Any]):
        srv = config_dict.get("server", {})
        self.server = ServerConfig(
            guild_id=int(os.getenv("DISCORD_GUILD_ID", srv.get("guild_id", 0))),
            owner_ids=[int(x) for x in srv.get("owner_ids", [])],
            name=srv.get("name", "OpenWinter"),
            tagline=srv.get("tagline", "Build together. Share freely.")
        )
        self.channels = ChannelsConfig(**config_dict.get("channels", {}))
        self.roles = RolesConfig(**config_dict.get("roles", {}))
        self.features = FeaturesConfig(**config_dict.get("features", {}))

        # Radio stations
        radio_data = config_dict.get("radio", {})
        self.default_station = radio_data.get("default_station", "lofi")
        self.stations: Dict[str, RadioStation] = {}
        for key, st_data in radio_data.get("stations", {}).items():
            self.stations[key] = RadioStation(**st_data)

        # AI
        self.ai = AIConfig(**config_dict.get("ai", {}))
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN", "")

def load_config(config_path: str = None) -> AppConfig:
    if not config_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        custom_cfg = os.path.join(base_dir, "config", "config.yaml")
        example_cfg = os.path.join(base_dir, "config", "config.example.yaml")
        config_path = custom_cfg if os.path.exists(custom_cfg) else example_cfg

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    return AppConfig(data)
