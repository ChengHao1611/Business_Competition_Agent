import os
import logging

from config import settings
from infra.linebot import create_app

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.WARN),
    format="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)

app = create_app("web")

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 5000)),
    )
