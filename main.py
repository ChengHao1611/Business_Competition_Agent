from agent import send_message_to_agent
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    get_response = send_message_to_agent("4", """
    https://sites.google.com/view/ncku-ilink/%E9%A6%96%E9%A0%81/
                          """, 4) 
    
    print(get_response)