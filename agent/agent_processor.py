from Linebot import linebot_reply_str as lrs
from pypdf import PdfReader
from .registry import states
from db.db import get_state, set_state
import time

import logging

logger = logging.getLogger(__name__)

def send_message_to_agent(user_id: str, user_message: str="", user_name: str="") -> str:
    """
    使用者傳入訊息，並根據當前使用者的狀態，進行處理後，傳LLM回覆的訊息

    參數:
        user_id: 使用者id
        user_message: 使用者傳的訊息

    回傳:
        str: LLM回覆的訊息

    """

    current_state = get_state(user_id, user_name)
    state = states[current_state]
    next_state, reply = state.execute(user_message)
    set_state(user_id, next_state)

    return reply

def receive_pdf_file(path: str):
    start_time = time.perf_counter()

    try:
        reader = PdfReader(str(path))
    except Exception as e:
        raise ValueError("failed to open PDF") from e
    open_time = time.perf_counter()

    texts = []
    total_chars = 0
    page_count = len(reader.pages)

    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
                total_chars += len(page_text)
        except Exception:
            logger.warning("failed to extract text from page %d | file=%s", i, path)
            continue

    extract_time = time.perf_counter()

    if not texts:
        raise ValueError("PDF contains no extractable text")

    full_text = "\n".join(texts)

    end_time = time.perf_counter()

    logger.info(
        "PDF parsed | file=%s | pages=%d | chars=%d | "
        "open=%.3fs | extract=%.3fs | total=%.3fs",
        path,
        page_count,
        total_chars,
        open_time - start_time,
        extract_time - open_time,
        end_time - start_time
    )

    return full_text