from agent.tool import *
from db.db_op import (get_user_message_history, 
                      set_user, set_user_state, 
                      set_user_competition, 
                      get_user_state)
import logging
from Linebot import lintbot_reply_str as lrs

logger = logging.getLogger(__name__)

def state1_find_competition(user_id: str, user_message: str) -> str:
    result = Tool.find_completion(user_id, user_message)
    if result == "出現莫名錯誤":
        result = lrs.error_warning
    result += lrs.check_competition
    set_user_state(user_id, "1-1")
    set_user_competition(user_id, user_message)
    return result

def state1_1_check_fit_competition(user_id, user_message: str) -> str:
    if user_message == "重新選擇競賽":
        result = lrs.find_new_competition
        set_user_state(user_id, "1")
    elif user_message == "確認適不適合參加這個競賽":
        result = lrs.confirm_fit_for_competition
        set_user_state(user_id, "1-2")
    elif user_message == "參加這個競賽":
        result = lrs.send_competition_proposal
        set_user_state(user_id, "2")
    else:
        result = lrs.error_warning

    return result