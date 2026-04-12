from __future__ import annotations

from core.ports.message_gateway import MessageGateway


class WebMessageGateway(MessageGateway):
    def __init__(self) -> None:
        self._messages: list[str] = []

    def reply_message(self, reply_token: str, text: str) -> None:
        self._messages.append(text)

    def push_message(self, user_id: str, text: str) -> None:
        self._messages.append(text)

    def drain_messages(self) -> list[str]:
        messages = list(self._messages)
        self._messages.clear()
        return messages

