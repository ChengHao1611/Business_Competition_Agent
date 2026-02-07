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

table_name = os.getenv("SUPABASE_TABLE_NAME")

res = supabase.table(table_name).select("*").limit(1).execute()

def create_user(user_id, user_name):
    data = {
        "line_id": user_id,
        "line_name": user_name,
        "current_state": "S0",
        "data": {
            "team_name": "AI小隊",
            "has_proposal": False
        }
    }

    res = supabase.table("user_history").insert(data).execute()
    logging.info(f"插入資料到資料庫: {res}")



if __name__ == "__main__":
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARN").upper()

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.WARN),
        format="%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
    )

    create_user("7788", "5566")