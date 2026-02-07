from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, FileMessage
import requests
import tempfile
import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from . import linebot_reply_str as lrs
from agent import send_message_to_agent, receive_pdf_file

PDF_SIZE = 20 #20MB

logger = logging.getLogger(__name__)

# Resolve keys.env relative to this file so loading doesn't depend on CWD
dotenv_path = Path(__file__).resolve().parent.parent / 'keys.env'
load_dotenv(dotenv_path=str(dotenv_path))

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# verify token
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = lrs.ADD_FRIEND_REPLY) # 歡迎訊息
    )

# handle messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
        將傳入的訊息交給agent來做判斷並回應
    """
    user_id = event.source.user_id
    user_message = event.message.text

    #result = send_message_to_agent(user_id, user_message)
    result = send_message_to_agent(user_id, user_message)
    
    reply_message_to_user(result, event.reply_token, user_id)


@handler.add(MessageEvent, message=FileMessage)
def handle_file(event):
    user_id = event.source.user_id
    message_id = event.message.id
    tmp_path = None
    file_size = event.message.file_size
    file_name = event.message.file_name

    # 檔案大小限制（例如 PDF_SIZE MB）
    if file_size > PDF_SIZE * 1024 * 1024:
        logging.warning("檔案超過2MB")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"檔案太大，請上傳 {PDF_SIZE}MB 以下的檔案")
        )
        return

    if Path(file_name).suffix.lower() != ".pdf":
        logging.warning("檔案不是PDF")
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="請上傳pdf檔")
        )
        return

    try:
        # 下載檔案
        headers = {
            "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
        }
        url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        # 建立暫存檔
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name

        logger.info(f"Temp file created: {tmp_path}")
    
        #交給 Agent
        result = receive_pdf_file(tmp_path)

        reply_message_to_user(result, event.reply_token, user_id)

    except Exception:
        logger.exception(f"File handler failed | user: {user_id} | file: {file_name} ")

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="處理檔案時發生錯誤，請稍後再試")
        )

    finally:
        # 不論成功或失敗都會執行
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
            logger.info(f"Temp file removed: {tmp_path}")


def reply_message_to_user(result: str, reply_token, user_id):
    if(len(result) > 4900):
        result = result[0:4900]

    try:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text = result)
        )
    except Exception as e:
        logger.warning("linebot reply_token失效")
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text = result)
        )


# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))