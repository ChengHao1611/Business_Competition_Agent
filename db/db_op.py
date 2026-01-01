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
        database="1141_compute_db"
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