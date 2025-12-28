from agent.tool import (Tool, initialize_user_history)
from db.db_op import get_user_message_history

import logging

logger = logging.getLogger(__name__)

def send_message_to_agent(user_name: str, user_message: str, mode: int) -> str:
    """
    使用者傳入提案內容，並選擇想要的模式，根據所選的模式進行處理後，傳LLM回覆的訊息

    參數:
        user_name: 使用者名字
        user_message: 使用者傳的訊息
        mode (int):
            1: 輸入競賽名稱
            2: 討論提案
            3: LLM 整理提案
            4: 輸入提案內容
    回傳:
        str: LLM回覆的訊息
    """
    if(len(get_user_message_history(user_name)) == 0):
        initialize_user_history(user_name)

    if mode == 1:
        return Tool.find_completion(user_name, user_message)
        #print(send_messages_to_LLM(messages))
    elif mode == 2:
        return Tool.discuss_proposal(user_name, user_message)
    elif mode == 3:
        return Tool.organize_proposal(user_name, user_message)
    elif mode == 4:
        return Tool.score_proposal(user_name, user_message)

    return "沒有選擇模式"