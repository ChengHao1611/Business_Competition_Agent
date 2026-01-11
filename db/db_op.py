import mysql.connector
from typing import List, Dict

# =========================
# DB 連線設定
# =========================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1141compute",
        database="1141compute_db"
    )


# =========================
# 1. 插入一筆訊息
# =========================
def set_user_message_history(user_name: str, role: str, message: str):
    print("INSERT MESSAGE : (", user_name, ") ", role, " : ", message)
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO messages (name, role, message)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (user_name, role, message))
    conn.commit()

    cursor.close()
    conn.close()


# =========================
# 2. 查詢某使用者所有訊息
# 回傳 List[dict[str, str]]
# =========================
def get_user_message_history(user_name: str) -> List[Dict[str, str]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT name, role, message
    FROM messages
    WHERE name = %s
    ORDER BY id
    """

    cursor.execute(sql, (user_name,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # 確保只回傳 string -> string
    result: List[Dict[str, str]] = []
    for r in rows:
        result.append({
            "name": r["name"],
            "role": r["role"],
            "message": r["message"]
        })

    return result


# =========================
# 3. 刪除某使用者所有訊息
# =========================
def clear_user_message_history(user_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "DELETE FROM messages WHERE name = %s"
    cursor.execute(sql, (user_name,))
    conn.commit()

    cursor.close()
    conn.close()

# =========================
# 4. 設置使用者
# =========================
def set_user(user_name: str, competition: str, state: str = "0"):
    print("INSERT MESSAGE : (", user_name, ") ", state, " : ", competition)
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO user (state, competition, name)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (state, competition, user_name))
    conn.commit()

    cursor.close()
    conn.close()


# =========================
# 5. 查詢某使用者狀態
# 回傳 int
# =========================
def get_user_state(user_name: str) -> str:
    """
        參數：使用者id

        回傳：int
        -1: 找不到使用者
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT state
    FROM user
    WHERE name = %s
    """

    cursor.execute(sql, (user_name,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    if result == None:
        return -1
    return result["state"]

# =========================
# 6. 設置某使用者狀態
# =========================
def set_user_state(user_name: str, user_state: int):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    UPDATE user
    SET state = %s
    WHERE name = %s
    """

    cursor.execute(sql, (user_state, user_name))
    conn.commit()

    cursor.close()
    conn.close()

# =========================
# 7. 查詢某使用者參加的競賽
# 回傳 int
# =========================
def get_user_competition(user_name: str) -> str:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT competition
    FROM user
    WHERE name = %s
    """

    cursor.execute(sql, (user_name,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    if result == None:
        return "no competition"
    return result["competition"]

# =========================
# 8. 設置某使用者參加的競賽
# =========================
def set_user_competition(user_name: str, user_competition: str):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    UPDATE user
    SET competition = %s
    WHERE name = %s
    """

    cursor.execute(sql, (user_competition, user_name))
    conn.commit()

    cursor.close()
    conn.close()

# =========================
# 9. 刪除某使用者
# =========================
def clear_user(user_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "DELETE FROM user WHERE name = %s"
    cursor.execute(sql, (user_name,))
    conn.commit()

    cursor.close()
    conn.close()