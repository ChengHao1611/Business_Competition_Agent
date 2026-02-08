from __future__ import annotations
import logging

from core.ports.message_gateway import MessageGateway
from core.ports.pdf_extractor import PdfExtractor
from app.flow_service import FlowService

logger = logging.getLogger(__name__)

class MessageService:
    def __init__(
        self,
        flow_service: FlowService,
        message_gateway: MessageGateway,
        pdf_extractor: PdfExtractor,
    ):
        self._flow_service = flow_service
        self._message_gateway = message_gateway
        self._pdf_extractor = pdf_extractor

    def handle_text(
        self,
        reply_token: str,
        user_id: str,
        text: str,
        user_name: str = "",
    ) -> str:
        transition = self._flow_service.handle_message(
            user_id=user_id,
            message=text,
            user_name=user_name,
        )
        replies = transition.replies
        if not replies:
            return ""

        first = replies[0]
        try:
            self._message_gateway.reply_message(reply_token, first)
        except Exception:
            logger.warning("%s Reply failed, attempting push", user_id)
            try:
                self._message_gateway.push_message(user_id, first)
            except Exception as push_error:
                logger.error("Push message failed for user %s: %s", user_id, str(push_error))

        for extra in replies[1:]:
            try:
                self._message_gateway.push_message(user_id, extra)
            except Exception as push_error:
                logger.error("Push message failed for user %s: %s", user_id, str(push_error))

        return "\n".join(replies)

    def handle_pdf(
        self,
        reply_token: str,
        user_id: str,
        file_path: str,
        user_name: str = "",
    ) -> str:
        text = self._pdf_extractor.extract_text(file_path)
        transition = self._flow_service.handle_message(
            user_id=user_id,
            message=text,
            user_name=user_name,
            metadata={"pdf_path": file_path, "pdf_text_len": len(text)},
        )
        replies = transition.replies
        if not replies:
            return ""

        first = replies[0]
        try:
            self._message_gateway.reply_message(reply_token, first)
        except Exception:
            logger.warning("%s Reply failed, attempting push", user_id)
            try:
                self._message_gateway.push_message(user_id, first)
            except Exception as push_error:
                logger.error("Push message failed for user %s: %s", user_id, str(push_error))

        for extra in replies[1:]:
            try:
                self._message_gateway.push_message(user_id, extra)
            except Exception as push_error:
                logger.error("Push message failed for user %s: %s", user_id, str(push_error))

        return "\n".join(replies)
