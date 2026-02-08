import os
import logging

from infra.linebot import app
from config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.WARN),
    format="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
