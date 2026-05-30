import json
import os
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI, APITimeoutError, APIError


_RETRY_ATTEMPTS = 3
_TIMEOUT_SECONDS = 30


class AIService:
    """
    Centralised OpenAI API client.

    Uses the openai >= 1.x SDK (OpenAI() client pattern).
    Supports:
    - Structured JSON responses (response_format=json_object)
    - Retries with exponential back-off
    - Configurable timeout
    - Graceful fallback when model returns invalid JSON
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY is not set. LLM calls will fail.")
        self._client = OpenAI(api_key=api_key, timeout=_TIMEOUT_SECONDS)
        self.model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """
        Synchronous LLM call with retries. Returns raw text content.
        Returns "" on unrecoverable error.
        """
        messages: List[Dict[str, str]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(1, _RETRY_ATTEMPTS + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except APITimeoutError:
                wait = 2 ** attempt
                print(f"[AIService] Timeout on attempt {attempt}. Retrying in {wait}s…")
                time.sleep(wait)
            except APIError as exc:
                print(f"[AIService] API error on attempt {attempt}: {exc}")
                if attempt == _RETRY_ATTEMPTS:
                    return ""
                time.sleep(2 ** attempt)
            except Exception as exc:
                print(f"[AIService] Unexpected error: {exc}")
                return ""

        return ""

    def call_llm_json(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        fallback: Optional[Any] = None,
    ) -> Any:
        """
        LLM call that forces JSON output (response_format=json_object).
        Parses and returns the JSON object.
        Returns `fallback` (default None) when parsing fails.
        """
        messages: List[Dict[str, str]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(1, _RETRY_ATTEMPTS + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                raw = response.choices[0].message.content or ""
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    print(f"[AIService] Invalid JSON from model: {raw[:200]}")
                    return fallback
            except APITimeoutError:
                wait = 2 ** attempt
                print(f"[AIService] Timeout (json) on attempt {attempt}. Retrying in {wait}s…")
                time.sleep(wait)
            except APIError as exc:
                print(f"[AIService] API error (json) on attempt {attempt}: {exc}")
                if attempt == _RETRY_ATTEMPTS:
                    return fallback
                time.sleep(2 ** attempt)
            except Exception as exc:
                print(f"[AIService] Unexpected error (json): {exc}")
                return fallback

        return fallback

    # Legacy async wrapper kept so existing callers don't break immediately.
    # New code should call call_llm() directly (synchronous).
    async def call_gpt(self, prompt: str, system_message: Optional[str] = None) -> str:
        return self.call_llm(prompt, system_message=system_message)
