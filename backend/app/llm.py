"""Thin wrapper around NVIDIA NIM (OpenAI-compatible API).

If no API key is configured, or the call fails, `chat` returns the provided
fallback text so the whole pipeline still runs offline for development and demos.
"""

import logging

from .config import settings

log = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI

        _client = OpenAI(base_url=settings.nvidia_base_url, api_key=settings.nvidia_api_key)
    return _client


def llm_enabled() -> bool:
    return bool(settings.nvidia_api_key)


def chat(system: str, user: str, fallback: str, temperature: float = 0.2, max_tokens: int = 600) -> str:
    if not llm_enabled():
        return fallback
    try:
        resp = _get_client().chat.completions.create(
            model=settings.nvidia_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or fallback
    except Exception as e:  # never let an LLM hiccup kill an investigation
        log.warning("LLM call failed, using fallback: %s", e)
        return fallback
