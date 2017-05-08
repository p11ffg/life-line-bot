import os
import time
from threading import Timer
import schedule
from bs4 import BeautifulSoup
import urllib
import urllib.request
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

dataid = "F-D0047-061"
authorizationkey = "CWB-BE234F8A-9F14-4069-A9F5-8795A3C20BC3"
url = "http://opendata.cwb.gov.tw/opendataapi?\
dataid={}&authorizationkey={}".format(dataid, authorizationkey)


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


def handleClient1():
    while(True):
        schedule.run_pending()
        time.sleep(5)


def handleClient2():
    weather_text = parse_weather()
    line_bot_api.push_message(USER_ID, TextSendMessage(text=weather_text))


def parse_weather():
    data = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(data, "xml")

    weather = soup.find("weatherElement")
    times = weather.find_all("time")
    results = []
    for time_child in times:
        result = time_child.find("value").text
        resultValue = int(result.replace(" ", ""))
        results.append(resultValue)
    max_value = max(results[0:8])
    min_value = min(results[0:8])
    result_text = "台北市今天最低溫: {}度, 最高溫: {}度".format(min_value, max_value)
    return result_text


schedule.every().day.at("08:30").do(handleClient2)
t = Timer(5.0, handleClient1)
t.start()


if __name__ == "__main__":
    app.run()
