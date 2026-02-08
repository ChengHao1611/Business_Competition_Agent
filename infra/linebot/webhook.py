from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FollowEvent, FileMessage

from app.flow_service import FlowService
from app.message_service import MessageService
from config import settings
from core.flow import FlowDeps, FlowRegistry, StateMachine
from infra.db.supabase_state_store import SupabaseStateStore
from infra.linebot.reply import LineBotMessageGateway
from infra.pdf.pypdf_extractor import PyPdfExtractor
from infra.llm.ollama_client import OllamaClient
from infra.web.crawl_web_page import SerpApiWebFetcher

logger = logging.getLogger(__name__)

PDF_SIZE_MB = 20

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

registry = FlowRegistry.from_yaml(settings.FLOW_CONFIG_PATH)
state_store = SupabaseStateStore(start_state=registry.start_state)
deps = FlowDeps(
    llm_client=OllamaClient(),
    web_fetcher=SerpApiWebFetcher(),
    pdf_extractor=PyPdfExtractor(),
)
state_machine = StateMachine(registry, deps)
flow_service = FlowService(state_store, state_machine)
message_gateway = LineBotMessageGateway(line_bot_api)
message_service = MessageService(flow_service, message_gateway, pdf_extractor=deps.pdf_extractor)


def _safe_reply(reply_token: str, user_id: str, text: str) -> None:
    try:
        message_gateway.reply_message(reply_token, text)
    except Exception as e:
        logger.warning("Reply failed: %s, attempting push", str(e))
        try:
            message_gateway.push_message(user_id, text)
        except Exception as push_error:
            logger.error("Push message failed for user %s: %s", user_id, str(push_error))


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    message_service.handle_text(event.reply_token, user_id, "")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    message_service.handle_text(event.reply_token, user_id, user_message)


@handler.add(MessageEvent, message=FileMessage)
def handle_file(event):
    user_id = event.source.user_id
    message_id = event.message.id
    tmp_path = None
    file_size = event.message.file_size
    file_name = event.message.file_name

    if file_size > PDF_SIZE_MB * 1024 * 1024:
        _safe_reply(event.reply_token, user_id, f"檔案太大，請上傳 {PDF_SIZE_MB}MB 以下的檔案")
        return

    if Path(file_name).suffix.lower() != ".pdf":
        _safe_reply(event.reply_token, user_id, "請上傳pdf檔")
        return

    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
        }
        url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name

        logger.info("Temp file created: %s", tmp_path)

        message_service.handle_pdf(event.reply_token, user_id, tmp_path)

    except Exception:
        logger.exception("File handler failed | user: %s | file: %s", user_id, file_name)
        _safe_reply(event.reply_token, user_id, "處理檔案時發生錯誤，請稍後再試")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
            logger.info("Temp file removed: %s", tmp_path)
