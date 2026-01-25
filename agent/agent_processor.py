from agent.tool import (Tool, initialize_user_history)
from db.db_op import (get_user_message_history, 
                      set_user,
                      get_user_state)
from Linebot import linebot_reply_str as lbr
from agent.state import *
from pypdf import PdfReader

import logging

logger = logging.getLogger(__name__)

def send_message_to_agent(user_id: str, user_message: str = "") -> str:
    """
    使用者傳入訊息，並根據當前使用者的狀態，進行處理後，傳LLM回覆的訊息

    參數:
        user_id: 使用者id
        user_message: 使用者傳的訊息

    回傳:
        str: LLM回覆的訊息

    state:
        0: 由LLM決定要使用哪個模式
        1: 輸入競賽名稱 => 回覆競賽資訊
        1-1: 確認適不適合參加這個競賽
        1-2: 回傳適不適合的結果
        1-3: 得到結果後，選擇要參加或放棄此競賽
        2: 輸入提案內容

    """
    #確認使用者的資訊有沒有儲存在SQL
    if get_user_state(user_id) == "-1":
        set_user(user_id, user_message, "1")
    if(len(get_user_message_history(user_id)) == 0):
        initialize_user_history(user_id)

    state = get_user_state(user_id)
    if state == "0":
        return Tool.LLM_choose_tool(user_id, user_message)
    elif state == "1":
        return state1_find_competition(user_id, user_message)
    elif state == "1-1":
        return state1_1_check_fit_competition(user_id, user_message)
    elif state == "1-2":
        return state1_2_answer_question_about_competition(user_id, user_message)
    elif state == "1-3":
        return state1_3_confirm_competition(user_id, user_message)
    elif state == "2":
        return Tool.score_proposal(user_id, user_message)

    logger.warning("狀態不存在")
    return lbr.error_warning

def receive_pdf_file(path: str):
    try:
        reader = PdfReader(str(path))
    except Exception as e:
        raise ValueError(f"failed to open PDF: {e}")

    texts = []
    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
        except Exception as e:
            raise ValueError(f"failed to extract text from page {i}: {e}")

    if not texts:
        raise ValueError("PDF contains no extractable text")

    return "\n".join(texts)