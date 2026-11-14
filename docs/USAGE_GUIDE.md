# SirDeep: Master Operator & User Guide

Welcome to the definitive user and operator guide for **SirDeep**. This manual covers everything from setting up your Discord bot application to running advanced autonomous security watchdogs, 24/7 coding radio streams, dynamic PIL card generation, and local AI backends.

---

## 📑 Table of Contents
1. [Prerequisites & Architecture](#1-prerequisites--architecture)
2. [Step 1: Discord Developer Portal Setup](#step-1-discord-developer-portal-setup)
3. [Step 2: Server Channels & Hierarchy Setup](#step-2-server-channels--hierarchy-setup)
4. [Step 3: Configuration Guide](#step-3-configuration-guide)
5. [Step 4: Module-by-Module Operational Guide](#step-4-module-by-module-operational-guide)
   * [AI Companion & Reasoning](#a-ai-companion--reasoning)
   * [24/7 Coding Radio Stream](#b-247-coding-radio-stream)
   * [Dynamic Contributor Leveling & Cards](#c-dynamic-contributor-leveling--cards)
   * [Audit Sentinel & Anti-Nuke Watchdog](#d-audit-sentinel--anti-nuke-watchdog)
   * [Daily Engineering Dilemmas](#e-daily-engineering-dilemmas)
6. [Step 5: Production Deployment (Docker & Systemd)](#step-5-production-deployment)
7. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## 1. Prerequisites & Architecture

Before starting, ensure your host environment meets the following specifications:
* **Operating System**: Linux (Ubuntu 20.04+, Debian 11+), macOS 12+, or Windows 10/11.
* **Python Runtime**: Python 3.11 or 3.12.
* **Audio Transcoder**: `ffmpeg` (required for radio playback).
* **Memory & Storage**: 512 MB RAM minimum (2 GB+ recommended if running local Ollama models).

---

## Step 1: Discord Developer Portal Setup

### 1.1 Create Your Application
1. Visit the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** in the top right.
3. Enter a name (e.g. `SirDeep`) and agree to the Developer Terms of Service.

### 1.2 Enable Privileged Gateway Intents (CRITICAL)
SirDeep requires Gateway intents to monitor audit events, welcome new members, track chat XP, and provide AI chat.

1. In the left menu, select **Bot**.
2. Scroll to the **Privileged Gateway Intents** section.
3. Toggle the following to **ON** (Blue):
   * ✅ **Server Members Intent**
   * ✅ **Message Content Intent**
4. Click **Save Changes**.

> [!WARNING]
> If you fail to enable these intents, the bot will immediately raise `discord.errors.PrivilegedIntentsRequired` upon startup.

### 1.3 Configure Bot Installation & Permissions
1. In the left menu, go to **OAuth2** $\rightarrow$ **URL Generator**.
2. Under **Scopes**, select:
   * ✅ `bot`
   * ✅ `applications.commands`
3. Under **Bot Permissions**, select:
   * ✅ `Manage Roles`
   * ✅ `Manage Channels`
   * ✅ `View Audit Log`
   * ✅ `View Channels` / `Read Messages`
   * ✅ `Send Messages`
   * ✅ `Embed Links`
   * ✅ `Attach Files`
   * ✅ `Read Message History`
   * ✅ `Connect` & `Speak` (Voice)
4. Copy the generated **OAuth2 URL** at the bottom and open it in your browser to invite SirDeep to your server.

### 1.4 Copy Your Bot Token
1. Go back to the **Bot** tab.
2. Click **Reset Token** (or **Copy**).
3. Save this token securely—you will paste it into your `.env` file.

---

## Step 2: Server Channels & Hierarchy Setup

For SirDeep's subsystems to function seamlessly, prepare the following channels in your server:

```text
📁 SECURITY & ADMINISTRATION (Locked Category)
   └── #audit-logs        (Private channel visible only to SirDeep & Admins)

📁 COMMUNITY & ONBOARDING
   └── #welcome           (Public welcome channel)
   └── #tech-debates      (Public forum or text channel for daily dilemmas)

📁 AUDIO LOUNGE
   └── 🔊 24/7 Coding Radio (Voice channel for continuous stream)
```

### Role Hierarchy Check
In your Discord server settings under **Roles**:
* Make sure the **SirDeep** bot role is positioned **higher** than the roles it needs to assign (e.g. `Builder`, `Core Contributor`).
* In Discord, a bot cannot manage or strip roles that are higher than its own highest role.

---

## Step 3: Configuration Guide

### 3.1 Setting Up Environment Variables (`.env`)
Create a `.env` file in the root directory by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```ini
# Discord Bot Credentials
DISCORD_BOT_TOKEN=MTE5OTg0...your_actual_bot_token...
DISCORD_GUILD_ID=123456789012345678

# AI Engine Provider (openrouter, gemini, openai, or ollama)
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-abcdef123456...

# Optional Providers
GEMINI_API_KEY=AIzaSy...
OPENAI_API_KEY=sk-...
OLLAMA_BASE_URL=http://localhost:11434

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 3.2 Setting Up Server Config (`config/config.yaml`)
Copy the example config:
```bash
cp config/config.example.yaml config/config.yaml
```

Key configuration options:
```yaml
guild:
  name: "OpenWinter"
  primary_color: 0x00d2ff
  accent_color: 0x10b981

channels:
  audit_logs: "audit-logs"
  welcome: "welcome"
  debates: "tech-debates"
  radio_voice: "24/7 Coding Radio"

security:
  anti_nuke:
    max_channel_deletions_per_minute: 3
    max_role_deletions_per_minute: 3
    quarantine_action: "strip_roles"

radio:
  default_station: "lofi"
  auto_reconnect: true

ai:
  provider: "openrouter"
  default_model: "anthropic/claude-3.5-sonnet"
  memory_ttl_seconds: 1800
  max_memory_messages: 10
```

---

## Step 4: Module-by-Module Operational Guide

### A. AI Companion & Reasoning
SirDeep acts as an intelligent engineering peer right in your server.

* **How to Chat**:
  * Mention the bot: `@SirDeep how do I optimize a SQLite WAL mode connection in Python?`
  * Reply to any of SirDeep's previous messages.
  * Use slash command: `/ask prompt:Explain Raft consensus in simple terms`.
* **Memory Management**:
  * SirDeep remembers conversation context for 30 minutes (`memory_ttl_seconds: 1800`).
  * Conversations are automatically pruned to prevent context overflow and token wastage.
* **Offline Local AI (Ollama)**:
  * Install [Ollama](https://ollama.ai) on your server: `ollama run llama3`.
  * Set `AI_PROVIDER=ollama` in `.env`. SirDeep will route all requests to your local GPU/CPU with **zero cloud cost**!

---

### B. 24/7 Coding Radio Stream
SirDeep provides an uninterrupted audio stream designed for deep focus work.

* **Available Stations**:
  * `lofi`: Relaxing chill lo-fi study beats.
  * `synthwave`: Cyberpunk retro electronic synthesizer streams.
  * `chillhop`: Instrumental jazz and hip-hop grooves.
  * `deepfocus`: Ambient binaural soundscapes for programming.
* **Commands & Controls**:
  * `/radio join`: Connects SirDeep to your current voice channel.
  * `/radio station <name>`: Switches the stream seamlessly without disconnecting.
  * `/radio stop`: Pauses playback and leaves the voice channel.
* **Auto-Reconnect**:
  * If the Discord voice connection drops due to packet loss, SirDeep automatically attempts reconnection with exponential backoff.

---

### C. Dynamic Contributor Leveling & Cards
Community members earn experience points (XP) for constructive technical discussions.

* **Earning Experience**:
  * Sending messages in technical channels grants between 15–25 XP (with a 60-second cooldown to prevent spam).
* **Viewing Rank & Profile**:
  * Run `/rank` or `/profile` in any text channel.
  * SirDeep generates and renders a high-definition (1000×520) glassmorphic card:
    * Displays real-time Level, Server Rank, and Total XP.
    * Progress bar showing percentage to the next tier.
    * Glowing status rings and anti-aliased circular Discord avatar.
* **Contributor Tiers**:
  * **Level 1–4**: `BUILDER`
  * **Level 5–14**: `CORE CONTRIBUTOR`
  * **Level 15+**: `SENIOR ARCHITECT`

---

### D. Audit Sentinel & Anti-Nuke Watchdog
SirDeep continuously watches the Discord Audit Log Gateway to safeguard your server.

* **Audit Logging**:
  * Captures and embeds events into `#audit-logs`:
    * Member Kicks & Bans (with moderator responsible and reason).
    * Member Timeouts / Timeouts lifted.
    * Role creation, permission updates, and role deletions.
    * Channel creation, name changes, topic updates, and deletions.
* **Anti-Nuke Protection**:
  * If any moderator account deletes more than 3 channels or roles within 60 seconds:
    1. SirDeep flags the actor immediately.
    2. Strips all administrative roles from the compromised moderator.
    3. Posts a high-priority red alert in `#audit-logs` tagging server owners.

---

### E. Daily Engineering Dilemmas
Fosters high-signal architectural debates in your community.

* Every day at 09:00 UTC (or via manual trigger `/debate post`), SirDeep selects a topic from `config/debates.json`:
  * *Microservices vs Monolith*
  * *Rust vs Go for High-Performance Backends*
  * *Postgres JSONB vs Native MongoDB*
  * *BEM vs Tailwind CSS*
* SirDeep automatically starts a dedicated discussion thread under the debate announcement so member discussions remain neat and indexed.

---

## Step 5: Production Deployment

### Option A: Docker Compose (Recommended)
This runs SirDeep in an isolated Linux container with pre-installed FFmpeg and TrueType fonts.

```bash
# Build and run in background
docker compose up -d --build

# View real-time log output
docker compose logs -f --tail=100

# Restart bot
docker compose restart

# Stop bot
docker compose down
```

### Option B: Linux Systemd Service
If you prefer running natively on an Ubuntu/Debian VPS:

1. Create a service file:
```bash
sudo nano /etc/systemd/system/sirdeep.service
```

2. Add the following configuration:
```ini
[Unit]
Description=SirDeep Community Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/sirdeep
ExecStart=/opt/sirdeep/.venv/bin/python /opt/sirdeep/main.py
Restart=always
RestartSec=10
EnvironmentFile=/opt/sirdeep/.env

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sirdeep
sudo systemctl start sirdeep
sudo systemctl status sirdeep
```

---

## Troubleshooting & FAQ

#### Q: Bot starts but crashes with `PrivilegedIntentsRequired`?
**A**: You forgot to enable **Server Members Intent** and **Message Content Intent** in the Discord Developer Portal. See [Step 1.2](#12-enable-privileged-gateway-intents-critical).

#### Q: Radio connects to the voice channel but there is no sound?
**A**: Ensure `ffmpeg` is installed on your system. Run `ffmpeg -version` in your terminal. On Ubuntu: `sudo apt install ffmpeg`. On Windows: `winget install Gyan.FFmpeg`.

#### Q: Cards are missing the custom font or showing standard font?
**A**: Ensure fonts are present in `assets/fonts/` or that standard system fonts (`Segoe UI` on Windows, `DejaVu Sans` on Linux) are installed. The Docker container includes all necessary fonts automatically.

#### Q: How do I change the default AI model?
**A**: In `config/config.yaml`, update `ai.default_model` to any model supported by your provider (e.g. `meta-llama/llama-3-70b-instruct` or `gpt-4o-mini`).

---

*Need more help? Join the [OpenWinter Discord Community](https://github.com/opensourcewinter) or open a GitHub Issue!*
