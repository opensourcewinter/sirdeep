# SirDeep by OpenWinter

SirDeep is an open-source Discord bot and community automation tool developed by OpenWinter. It provides developer-oriented features such as AI chat, 24/7 coding radio, architecture debate discussions, audit logging, and anti-nuke protection.

## Features

- **AI Companion**: Interactive developer chat using cloud or local Ollama models.
- **Audit Logging**: Real-time logging of kicks, bans, timeouts, and channel edits to `#audit-logs`.
- **Anti-Nuke Protection**: Automatic rate-limiting on channel and role deletions.
- **24/7 Coding Radio**: Multi-station stream for Lo-Fi, Synthwave, and Deep Focus audio.
- **Architecture Debates**: Automated daily technical discussions with dedicated threads.
- **Contributor Leveling**: Experience tracking and custom profile card generation.

## Getting Started

1. Copy `.env.example` to `.env` and provide your `DISCORD_BOT_TOKEN`.
2. Copy `config/config.example.yaml` to `config/config.yaml` and set your server details.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run: `python main.py`.

Or launch with Docker: `docker compose up -d`.

## License

MIT License. OpenWinter.
