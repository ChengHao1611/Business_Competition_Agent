from . import proposal_template as pt

def  send_message_to_agent(user_name: str, user_message: str, mode: int) -> str:
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
    if mode == 1:
        #clear_user_message_history(user_name)
        #implement get_user_message_history(user_name: str, role: str) -> str(user_message_history):
        print(f"找到{user_message}競賽")
        result_message = f"找到{user_message}競賽" + pt.system_rule
    elif mode == 2:
        #implement get_user_message_history(user_name: str, role: str) -> str(user_message_history):
        # 新增模板
        # 傳給LLM
        # 接收LLM結果
        # 在database 紀錄
        print("LLM回傳的結果")
        result_message = "LLM回傳的結果"
    elif mode == 3:
        #implement get_user_message_history(user_name: str, role: str) -> str(user_message_history):
        # 新增模板
        # 傳給LLM
        # 接收LLM結果
        # 在database 紀錄
        print("LLM回傳整理的提案")
        result_message = "LLM回傳整理的提案"
    elif mode == 4:
        #implement get_user_message_history(user_name: str, role: str) -> str(user_message_history):
        # 新增模板
        # 傳給LLM
        # 接收LLM結果
        # 在database 紀錄
        print("LLM回傳提案評分")
        result_message = "LLM回傳提案評分"
        


    return result_message