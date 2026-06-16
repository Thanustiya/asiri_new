# backend/services/ollama_service.py
"""
Local Ollama integration for free AI chat support.
Configured for concise Asiri Perera website and general-help answers.
"""

import httpx
import logging
import asyncio
from typing import Optional
from config import settings
from services.knowledge_base import OLLAMA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        user_message: str,
        conversation_history: Optional[list] = None,
        knowledge_hint: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a response from the configured local Ollama model.
        Returns None if Ollama is unavailable.
        """
        if not await self.is_available():
            logger.warning("Ollama is not available")
            return None

        # Build messages
        messages = [{"role": "system", "content": OLLAMA_SYSTEM_PROMPT}]
        if knowledge_hint:
            messages.append({
                "role": "system",
                "content": "Most relevant site knowledge for this question:\n" + knowledge_hint
            })

        # Add recent history (last 4 exchanges to stay fast)
        if conversation_history:
            recent = conversation_history[-8:]  # last 4 pairs
            for msg in recent:
                messages.append({
                    "role": msg["role"] if msg["role"] != "bot" else "assistant",
                    "content": msg["content"]
                })

        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "temperature": 0.3,      # Low temp = more factual
                "num_predict": 180,      # Shorter local answers respond faster
                "top_k": 10,
                "top_p": 0.9,
                "stop": ["\n\n\n", "Human:", "User:"]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Calling Ollama {self.model}...")
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "").strip()
                logger.info(f"Ollama response: {content[:100]}...")
                return content if content else None
        except httpx.TimeoutException:
            logger.error(f"Ollama timeout after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return None

    async def generate_with_typing(
        self,
        user_message: str,
        conversation_history: Optional[list] = None,
        knowledge_hint: Optional[str] = None,
        on_token=None
    ):
        """
        Streaming version — yields tokens as they arrive.
        This makes the response feel faster even if total time is same.
        """
        if not await self.is_available():
            return None

        messages = [{"role": "system", "content": OLLAMA_SYSTEM_PROMPT}]
        if knowledge_hint:
            messages.append({
                "role": "system",
                "content": "Most relevant site knowledge for this question:\n" + knowledge_hint
            })

        if conversation_history:
            recent = conversation_history[-8:]
            for msg in recent:
                messages.append({
                    "role": msg["role"] if msg["role"] != "bot" else "assistant",
                    "content": msg["content"]
                })

        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "keep_alive": "10m",
            "options": {
                "temperature": 0.3,
                "num_predict": 180,
                "top_k": 10,
            }
        }

        full_response = ""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST", f"{self.base_url}/api/chat", json=payload
                ) as response:
                    import json
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                token = chunk.get("message", {}).get("content", "")
                                if token:
                                    full_response += token
                                    if on_token:
                                        await on_token(token)
                                if chunk.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")

        return full_response.strip() if full_response else None


ollama_service = OllamaService()