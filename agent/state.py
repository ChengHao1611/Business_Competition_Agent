from agent.tool import *
from db.db_op import (get_user_message_history, 
                      set_user, set_user_state, 
                      set_user_competition, 
                      get_user_state)
import logging
from Linebot import linebot_reply_str as lrs

logger = logging.getLogger(__name__)

def state1_find_competition(user_id: str, user_message: str) -> str:
    result = Tool.find_competition(user_id, user_message)
    if result == "出現莫名錯誤":
        return lrs.ERROR_WARNING + "\n\n請再次輸入比賽名稱"
    result += lrs.FIND_COMPETITION
    set_user_state(user_id, "1-1")
    set_user_competition(user_id, user_message)
    return result

def state1_1_check_fit_competition(user_id, user_message: str) -> str:
    if user_message == "重新選擇競賽":
        result = lrs.FIND_NEW_COMPETITION
        set_user_state(user_id, "1")
    elif user_message == "確認適不適合參加這個競賽":
        result = lrs.CONFIRM_FIT_FOR_COMPETITION
        set_user_state(user_id, "1-2")
    elif user_message == "參加這個競賽":
        result = lrs.SEND_COMPETITION_PROPOSAL
        set_user_state(user_id, "2")
    else:
        result = lrs.ERROR_WARNING + lrs.FIND_COMPETITION

    return result

def state1_2_answer_question_about_competition(user_id: str, user_message: str) -> str:
    result = Tool.fit_competition(user_id, user_message)
    if result == "出現莫名錯誤":
        result = lrs.ERROR_WARNING
    set_user_state(user_id, "1-3")
    return result + lrs.REPLY_SUITABLE_FOR_COMPETITION

def state1_3_confirm_competition(user_id: str, user_message: str) -> str:
    if user_message == "重新選擇競賽":
        result = lrs.FIND_NEW_COMPETITION
        set_user_state(user_id, "1")
    elif user_message == "參加這個競賽":
        result = lrs.SEND_COMPETITION_PROPOSAL
        set_user_state(user_id, "2")
    else:
        result = lrs.ERROR_WARNING + lrs.REPLY_SUITABLE_FOR_COMPETITION

    return result