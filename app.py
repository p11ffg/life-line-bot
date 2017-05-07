import os
import schedule
import time
import datetime
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
YOUR_CHANNEL_ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
YOUR_CHANNEL_SECRET = os.environ.get("SECRET")

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

USER_ID = "U7fc6670c8ae890fcaf33f99a9796fcfc"


@app.route("/")
def hello():
    return "hello"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK', 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("user_id:", event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


def job():
    line_bot_api.push_message(USER_ID, TextSendMessage(text="Hello World!"))


# schedule.every().day.at("00:09").do(job)
# while True:
#     schedule.run_pending()
#     time.sleep(1)


if __name__ == "__main__":
    app.run()
