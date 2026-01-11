from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from agent import send_message_to_agent
import os
from pathlib import Path
from dotenv import load_dotenv
from . import lintbot_reply_str
from .user import User

# Resolve keys.env relative to this file so loading doesn't depend on CWD
dotenv_path = Path(__file__).resolve().parent.parent / 'keys.env'
load_dotenv(dotenv_path=str(dotenv_path))

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
users = {}

def get_user(user_id) -> User:
    if user_id not in users:
        user = User(user_id)
        users[user_id] = {
            "id": user_id,
            "User": user
        }
    return users[user_id]["User"]

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
        TextSendMessage(text = lintbot_reply_str.add_friend_reply) # 歡迎訊息
    )

# handle messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
        將傳入的訊息交給agent來做判斷並回應
    """
    user_id = event.source.user_id
    user = get_user(user_id)
    competition_name = user.competition
    mode = user.mode
    user_message = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=user_message)
    )
    # if mode == -1: # waiting for mode selection
    #     if user_message == '1': # input competition name
    #         user_state['mode'] = 1 
    #         user_state['competition_name'] = ''
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text='切換到mode 1') # 回應訊息
    #         )
    #     elif user_message == '2': # discuss proposal
    #         if competition_name == '':
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text='請先輸入競賽名稱') # 回應訊息
    #             )
    #             line_bot_api.push_message(
    #                 user_id,
    #                 TextSendMessage(text='請選擇您想要使用的功能\n1. 輸入競賽名稱\n2. 與LLM討論提案內容\n3. 由LLM整理提案\n4. 輸入提案內容\n')
    #             )
    #             return
    #         else:
    #             user_state['mode'] = 2
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text='如果想要停止討論，請輸入end') # 回應訊息
    #             )
    #     elif user_message == '3': # organize proposal
    #         if competition_name == '':
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text='請先輸入競賽名稱') # 回應訊息
    #             )
    #             line_bot_api.push_message(
    #                 user_id,
    #                 TextSendMessage(text='請選擇您想要使用的功能\n1. 輸入競賽名稱\n2. 與LLM討論提案內容\n3. 由LLM整理提案\n4. 輸入提案內容\n')
    #             )
    #             return
    #         else:
    #             user_state['mode'] = 3
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text='正在整理提案內容，請稍候...')
    #             )
    #             result = send_message_to_agent(user_id, event.message.text, user_state['mode'])
    #             line_bot_api.push_message(
    #                 user_id,
    #                 TextSendMessage(text=result) # 回應訊息
    #             )
    #             user_state['mode'] = -1
    #             line_bot_api.push_message(
    #                 user_id,
    #                 TextSendMessage(text='請選擇您想要使用的功能\n1. 輸入競賽名稱\n2. 與LLM討論提案內容\n3. 由LLM整理提案\n4. 輸入提案內容\n')
    #             )
    #     elif user_message == '4': # input proposal content
    #         if competition_name == '':
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text='請先輸入競賽名稱') # 回應訊息
    #             )
    #             line_bot_api.push_message(
    #                 user_id,
    #                 TextSendMessage(text='請選擇您想要使用的功能\n1. 輸入競賽名稱\n2. 與LLM討論提案內容\n3. 由LLM整理提案\n4. 輸入提案內容\n')
    #             )
    #             return
    #         else:
    #             user_state['mode'] = 4
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text='切換到mode 4') # 回應訊息
    #             )
    #     else:
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text='正在等待LLM回應，請稍候...')
    #         )
    #         result = send_message_to_agent(user_id, event.message.text, 0)
    #         line_bot_api.push_message(
    #             user_id,
    #             TextSendMessage(text=result) # 回應訊息
    #         )
    # elif mode == 2:
    #     if user_message == 'end':
    #         user_state['mode'] = -1
    #         line_bot_api.push_message(
    #             user_id,
    #             TextSendMessage(text='請選擇您想要使用的功能\n1. 輸入競賽名稱\n2. 與LLM討論提案內容\n3. 由LLM整理提案\n4. 輸入提案內容\n')
    #         )
    #     else:
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage(text='正在等待LLM回應，請稍候...')
    #         )
    #         result = send_message_to_agent(user_id, event.message.text, user_state['mode'])
    #         line_bot_api.push_message(
    #             user_id,
    #             TextSendMessage(text=result) # 回應訊息
    #         )
    # elif mode == 1:
    #     user_state['competition_name'] = user_message
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='正在整理比賽資訊，請稍候...')
    #     )
    #     result = send_message_to_agent(user_id, user_state['competition_name'], user_state['mode'])
    #     line_bot_api.push_message(
    #         user_id,
    #         TextSendMessage(text=result) # 回應訊息
    #     )
    #     user_state['mode'] = -1
    #     line_bot_api.push_message(
    #         user_id,
    #         TextSendMessage(text='請選擇您想要使用的功能\n1. 輸入競賽名稱\n2. 與LLM討論提案內容\n3. 由LLM整理提案\n4. 輸入提案內容\n')
    #     )
    # elif mode == 4:
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text='正在等待LLM評分與建議，請稍候...')
    #     )
    #     result = send_message_to_agent(user_id, event.message.text, user_state['mode'])
    #     line_bot_api.push_message(
    #         user_id,
    #         TextSendMessage(text=result) # 回應訊息
    #     )
    #     user_state['mode'] = -1
    #     line_bot_api.push_message(
    #         user_id,
    #         TextSendMessage(text='請選擇您想要使用的功能\n1. 輸入競賽名稱\n2. 與LLM討論提案內容\n3. 由LLM整理提案\n4. 輸入提案內容\n')
    #     )


# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))