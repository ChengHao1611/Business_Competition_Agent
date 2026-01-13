from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
import os
from pathlib import Path
from dotenv import load_dotenv
from . import lintbot_reply_str as lbr
from agent import send_message_to_agent

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
        TextSendMessage(text = lbr.add_friend_reply) # 歡迎訊息
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
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = result)
        )
    except:
        line_bot_api.push_message(
        user_id,
        TextSendMessage(text = result)
        )

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))