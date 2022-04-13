from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
import os
from dotenv import load_dotenv
from .service.uniqlo_service import UniqloService

load_dotenv()
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

app = Flask(__name__)


@app.route("/text", methods=["GET"])
def text():
    print(request.headers)
    print("---")
    print(request.args.to_dict())
    print("---")
    # get request body as text
    body = request.get_data(as_text=True)
    print(body)

    return "<html><body><h1>Hello World</h1></body></html>"


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id

    if event.message.text == "發送訊息":
        ## DO SEND NOTIFICATION TO EACH USER
        print()
    elif event.message.text.isnumeric():
        reply_message = UniqloService(
            user_id=user_id,
            message=str(event.message.text)
        ).get_current_price()
    else:
        reply_message = TextSendMessage(
            text="Unknown command, please contact ericlynn0912@gmail.com to get more information."
        )
    line_bot_api.reply_message(event.reply_token, reply_message)


if __name__ == "__main__":
    app.run()
