# test_op.py
from db_op import *

def main():
    user = "Bob"

    print("=== 清空舊資料 ===")
    clear_user_message_history(user)

    print("=== 插入三筆資料 ===")
    set_user_message_history(user, "user", "Hello")
    set_user_message_history(user, "user", "How are you?")
    set_user_message_history(user, "assistant", "I'm fine")

    print("=== 查詢 Bob 的所有訊息（應該有 3 筆） ===")
    history = get_user_message_history(user)

    for msg in history:
        print(msg)

    print(f"總筆數: {len(history)}")

    print("=== 刪除 Bob 的所有訊息 ===")
    clear_user_message_history(user)

    print("=== 再次查詢（應該是空的） ===")
    history = get_user_message_history(user)
    print(history)
    print(f"總筆數: {len(history)}")

    print("=== 清空舊資料 ===")
    clear_user(user)

    print("=== 插入使用者資訊 ===")
    #set_user(user, "創見南方")

    print("=== 得到使用者狀態 ===")
    print(get_user_state(user))

    print("=== 修改使用者狀態 ===")
    set_user_state(user, 1)
    print(get_user_state(user))

    print("=== 得到競賽資訊 ===")
    print(get_user_competition(user))

    print("=== 設置競賽資訊 ===")
    set_user_competition(user, "dd")
    print(get_user_competition(user))

    print("=== 清空舊資料 ===")
    clear_user(user)

if __name__ == "__main__":
    main()