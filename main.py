from agent import send_message_to_agent
import os
from Linebot import app
import logging

logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    get_response = send_message_to_agent("4", """
    創見南方
                          """, 2) 
    
    print(get_response)
    #app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))