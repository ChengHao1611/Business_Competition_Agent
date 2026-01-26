import os
from Linebot import app
import logging

logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))