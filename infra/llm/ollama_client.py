from __future__ import annotations

import json
import logging
import re

from ollama import Client

from config import settings
from core.ports.llm_client import LLMClient

logger = logging.getLogger(__name__)


class OllamaClient(LLMClient):
    def __init__(self):
        self._api_key = settings.get_env("OLLAMA_API_KEY") or ""

    def send_messages(self, messages: list[dict[str, str]]) -> str:
        client = Client(
            host="https://ollama.com",
            headers={"Authorization": "Bearer " + self._api_key},
        )

        logger.info("等待ollama回應")
        try:
            for part in client.chat("gpt-oss:120b", messages=messages, stream=False):
                if part[0] == "message":
                    logger.info(part)
                    return part[1]["content"]
        except Exception as e:
            _error_process(e)
            return "LLM接收/回覆出現問題"


def _error_process(e: Exception) -> None:
    detail = None
    if isinstance(e, dict):
        detail = e.get("detail")
    else:
        detail = getattr(e, "detail", None)
        if detail is None and hasattr(e, "args") and e.args:
            first = e.args[0]
            if isinstance(first, dict):
                detail = first.get("detail")
            elif isinstance(first, str):
                try:
                    parsed = json.loads(first)
                    if isinstance(parsed, dict):
                        detail = parsed.get("detail")
                except Exception:
                    m = re.search(r'"detail":\s*"([^"]+)"', first)
                    if m:
                        detail = m.group(1)

    if detail == "Invalid API Key" or (detail is None and "Invalid API Key" in str(e)):
        logger.warning("LLM的API錯誤")
    else:
        logger.exception("LLM接收/回覆出現問題")

