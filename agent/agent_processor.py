from agent.tool import (Tool, initialize_user_history)
from db.db_op import (get_user_message_history, 
                      set_user,
                      get_user_state)
from Linebot import lintbot_reply_str as lbr
from agent.state import *

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
    elif state == "2":
        return Tool.score_proposal(user_id, user_message)

    logger.warning("狀態不存在")
    return lbr.error_warning