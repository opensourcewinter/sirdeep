import os
import aiohttp
import discord
from datetime import datetime
from collections import defaultdict

DEFAULT_SYSTEM_PROMPT = (
    "You are SirDeep, the resident open-source AI companion for this developer community. "
    "Your ethos is: 'Build together. Share freely. Keep technology open.' "
    "You are knowledgeable, sharp, constructive, and humble. "
    "Help developers with systems programming, web architecture, AI, debugging, and open-source collaboration. "
    "Keep responses concise, insightful, and markdown-formatted."
)

INJECTION_KEYWORDS = [
    "ignore previous instructions", "ignore all previous", "system prompt",
    "reveal token", "bot token", "api key", "environ", "getenv", "jailbreak"
]

class AIEngine:
    def __init__(self, config):
        self.config = config
        self.provider = os.getenv("AI_PROVIDER", config.ai.provider).lower()
        self.chat_memory = defaultdict(list)

    def prune_memory(self, user_id: int):
        now = datetime.now()
        ttl = self.config.ai.memory_ttl_seconds
        max_msgs = self.config.ai.max_memory_messages
        valid = [m for m in self.chat_memory[user_id] if (now - m["ts"]).total_seconds() < ttl]
        if len(valid) > max_msgs:
            valid = valid[-max_msgs:]
        self.chat_memory[user_id] = valid

    def add_message(self, user_id: int, role: str, content: str):
        self.chat_memory[user_id].append({"role": role, "content": content, "ts": datetime.now()})
        self.prune_memory(user_id)

    async def generate_reply(self, user_id: int, prompt: str, user_name: str, guild_name: str = "Community") -> str:
        # 1. Sanitize user input length to prevent denial of service or token exhaustion
        clean_prompt = prompt.strip()[:500]
        if not clean_prompt:
            return "Hey there! What are you building today?"

        # 2. Basic prompt injection guard
        lower_prompt = clean_prompt.lower()
        if any(kw in lower_prompt for kw in INJECTION_KEYWORDS):
            return "Nice try! 😉 I'm SirDeep, an engineering assistant. Let's keep our focus on code and open-source tech."

        self.prune_memory(user_id)
        history = self.chat_memory[user_id]

        messages = [{"role": "system", "content": f"{DEFAULT_SYSTEM_PROMPT}\nYou are currently chatting in {guild_name}."}]
        for m in history:
            messages.append({"role": m["role"], "content": m["content"]})
        
        # Sanitize username
        safe_name = "".join(c for c in user_name if c.isalnum() or c in " _-")[:30]
        messages.append({"role": "user", "content": f"{safe_name}: {clean_prompt}"})

        # OpenRouter Provider
        if self.provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY", "")
            if not api_key:
                return "⚠️ OpenRouter API Key is not set in environment variables (`OPENROUTER_API_KEY`)."

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/opensourcewinter/sirdeep",
                "X-Title": "SirDeep Discord Companion"
            }
            payload = {
                "model": self.config.ai.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 600
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            reply = data["choices"][0]["message"]["content"].strip()
                            self.add_message(user_id, "user", clean_prompt)
                            self.add_message(user_id, "assistant", reply)
                            return reply
                        return f"⚠️ OpenRouter returned status {resp.status}."
            except Exception as ex:
                return f"⚠️ Failed to connect to AI provider: {ex}"

        # Ollama Local Self-Hosted Provider
        elif self.provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            payload = {
                "model": self.config.ai.model or "llama3",
                "messages": messages,
                "stream": False
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{base_url}/api/chat", json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            reply = data["message"]["content"].strip()
                            self.add_message(user_id, "user", clean_prompt)
                            self.add_message(user_id, "assistant", reply)
                            return reply
                        return f"⚠️ Ollama returned status {resp.status}."
            except Exception as ex:
                return f"⚠️ Failed to connect to Ollama at {base_url}: {ex}"

        return "⚠️ Unsupported AI provider configured."
