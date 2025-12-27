from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from agent import send_message_to_agent
from dotenv import load_dotenv
load_dotenv(dotenv_path='../keys.env')
import os

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
        TextSendMessage(text='你好，這裡是競賽小幫手\n') # 歡迎訊息
    )

# handle messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id 
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='正在計算分數並給予意見，請稍候...')
    )
    result = send_message_to_agent(user_id, event.message.text, 2)
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text=result) # 回應訊息
    )

if __name__ == '__main__':
    app.run(port=5000)