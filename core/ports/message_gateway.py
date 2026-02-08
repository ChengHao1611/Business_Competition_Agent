from __future__ import annotations

from abc import ABC, abstractmethod


class MessageGateway(ABC):
    @abstractmethod
    def reply_message(self, reply_token: str, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def push_message(self, user_id: str, text: str) -> None:
        raise NotImplementedError

