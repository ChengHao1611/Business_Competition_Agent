from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def send_messages(self, messages: list[dict[str, str]]) -> dict:
        raise NotImplementedError

