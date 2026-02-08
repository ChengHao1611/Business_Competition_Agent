from __future__ import annotations

from linebot import LineBotApi
from linebot.models import TextSendMessage

from core.ports.message_gateway import MessageGateway


class LineBotMessageGateway(MessageGateway):
    def __init__(self, line_bot_api: LineBotApi, max_chars: int = 4900):
        self._line_bot_api = line_bot_api
        self._max_chars = max_chars

    def reply_message(self, reply_token: str, text: str) -> None:
        safe_text = text[: self._max_chars]
        self._line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=safe_text),
        )

    def push_message(self, user_id: str, text: str) -> None:
        safe_text = text[: self._max_chars]
        self._line_bot_api.push_message(
            user_id,
            TextSendMessage(text=safe_text),
        )
