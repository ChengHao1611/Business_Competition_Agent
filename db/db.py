from dotenv import load_dotenv
import os
from supabase import create_client
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
dotenv_path = Path(__file__).resolve().parent.parent / 'keys.env'
load_dotenv(dotenv_path=str(dotenv_path))

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SECRET_KEY")
)

TABLE_NAME = os.getenv("SUPABASE_TABLE_NAME")
START_STATE = "S0_welcome"

res = supabase.table(TABLE_NAME).select("*").limit(1).execute()

def create_user(user_id: str, user_name: str):
    try:
        data = {
            "line_id": user_id,
            "line_name": user_name,
            "current_state": START_STATE,
            "data": {
                "team_name": "AI小隊",
                "has_proposal": False
            }
        }

        res = supabase.table(TABLE_NAME).insert(data).execute()
        logging.info(f"{user_id} 建立成功")
    except Exception as e:
        logging.exception(f"{user_id} 建立失敗")
        raise

def get_state(user_id: str, user_name: str) -> str:
    try:
        # 先嘗試拿資料
        res = (
            supabase
            .table(TABLE_NAME)
            .select("current_state")
            .eq("line_id", user_id)
            .single()
            .execute()
        )

        state = res.data["current_state"]
        logging.info(f"取得使用者狀態: {user_id} -> {state}")
        return state

    except Exception as e:
        logging.warning(
            f"使用者不存在，建立新使用者: {user_id}"
        )

        create_user(user_id, user_name)

        return START_STATE
    
def set_state(user_id: str, new_state: str):
    res = (
        supabase
        .table(TABLE_NAME)
        .update({"current_state": new_state})
        .eq("line_id", user_id)
        .execute()
    )




if __name__ == "__main__":
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARN").upper()

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.WARN),
        format="%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
    )

    create_user("7788", "5566")