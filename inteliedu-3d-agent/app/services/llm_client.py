"""Async LLM adapter supporting Groq, Gemini, and OpenAI-compatible endpoints."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List, Optional

import httpx

from app.config import Settings, get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def _extract_json_block(raw_text: str) -> Any:
    """Parse JSON from raw LLM text, stripping optional markdown fences."""
    cleaned = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try extracting first JSON object or array
        obj_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if obj_match:
            return json.loads(obj_match.group(1))
        raise


class LLMClient:
    """Thin async wrapper around configured LLM providers with retries and fallback."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.effective_llm_config().get("api_key"))

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout: float = 30.0,
    ) -> Optional[Dict[str, Any]]:
        """Call configured LLM expecting a JSON object; returns None when unconfigured or unreachable."""
        cfg = self.settings.effective_llm_config()
        api_key = cfg.get("api_key")
        if not api_key:
            return None

        provider = (cfg.get("provider") or "groq").lower()
        models: List[str] = []
        if cfg.get("model"):
            models.append(cfg["model"])
        if cfg.get("fallback_model") and cfg["fallback_model"] not in models:
            models.append(cfg["fallback_model"])

        for model_name in models:
            for attempt in range(2):
                try:
                    if provider == "gemini":
                        raw = await self._call_gemini(
                            api_key=api_key,
                            model=model_name,
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            timeout=timeout,
                        )
                    else:
                        raw = await self._call_openai_compat(
                            url=GROQ_CHAT_URL,
                            api_key=api_key,
                            model=model_name,
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            timeout=timeout,
                        )
                    parsed = _extract_json_block(raw)
                    if isinstance(parsed, dict):
                        return parsed
                except (httpx.HTTPError, ValueError, json.JSONDecodeError) as exc:
                    logger.warning(
                        "LLM JSON call failed (provider=%s, model=%s, attempt=%s): %s",
                        provider,
                        model_name,
                        attempt + 1,
                        exc,
                    )
                    if attempt == 0:
                        await asyncio.sleep(0.8)
        return None

    async def _call_openai_compat(
        self,
        url: str,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def _call_gemini(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "responseMimeType": "application/json",
            },
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, params={"key": api_key}, json=payload)
            resp.raise_for_status()
            data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts)

