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


@app.route("/subscribe", methods=["GET"])
def subscribe():
    # get request body as text
    data = request.args.to_dict()
    reply_message = UniqloService().subscribe(data)

    return f'<html><body><h1>{reply_message}<br>等待 3 秒後跳轉...</h1><script>setTimeout(function(){{window.location.href = "https://line.me/R/";}},3000);</script></body></html>'

@app.route("/subscribe-v2", methods=["GET"])
def subscribe_v2():
    # get request body as text
    data = request.args.to_dict()
    reply_message = UniqloService().subscribe_v2(data)
    check_img = os.getenv("CHECK_IMAGE")
    return f"""<table width="100%" height="100">
    <tr><td align="center" valign="center"><img src="{check_img}" alt=""  height=100 width=100></td></tr>
    <tr><td align="center" valign="center"><font color="#696969" font size="10">{reply_message}</font></td></tr>
    <tr><td align="center" valign="center"><font color="#696969" font size="6">等待 2 秒後關閉</font></td></tr>
    <tr><td align="center" valign="center"><font color="#696969" font size="6">(如未關閉請自行點擊關閉鈕)</font></td></tr>
    </table>
    <script>setTimeout(function(){{window.close();}},2000);</script>"""

@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    # get request body as text
    data = request.args.to_dict()
    reply_message = UniqloService().unsubscribe(data)

    return f'<html><body><h1>{reply_message}<br>等待 3 秒後跳轉...</h1><script>setTimeout(function(){{window.location.href = "https://line.me/R/";}},3000);</script></body></html>'

@app.route("/unsubscribe-v2", methods=["GET"])
def unsubscribe_v2():
    # get request body as text
    data = request.args.to_dict()
    reply_message = UniqloService().unsubscribe_v2(data)

    check_img = os.getenv("CHECK_IMAGE")
    return f"""<table width="100%" height="100">
    <tr><td align="center" valign="center"><img src="{check_img}" alt=""  height=100 width=100></td></tr>
    <tr><td align="center" valign="center"><font color="#696969" font size="10">{reply_message}</font></td></tr>
    <tr><td align="center" valign="center"><font color="#696969" font size="6">等待 2 秒後關閉</font></td></tr>
    <tr><td align="center" valign="center"><font color="#696969" font size="6">(如未關閉請自行點擊關閉鈕)</font></td></tr>
    </table>
    <script>setTimeout(function(){{window.close();}},2000);</script>"""

@app.route("/wake-up", methods=["GET"])
def wakeup():

    return "I've got up."

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

    if event.message.text == "發送每日通知訊息":
        ## DO SEND NOTIFICATION TO EACH USER
        reply_message = UniqloService(user_id=user_id).send_notification()
    elif event.message.text == "設定排程":
        reply_message = UniqloService(user_id=user_id).cron_setter()
    elif event.message.text.isnumeric():
        reply_message = UniqloService(
            user_id=user_id,
            message=str(event.message.text)
        ).get_current_price()
    elif event.message.text == "我的追蹤清單":
        reply_message = UniqloService(
            user_id=user_id,
            message=str(event.message.text)
        ).get_subscription_list()
    elif event.message.text == "查價教學":
        reply_message = TextMessage(
            text = """🔥 小偵探這就來教大家掌握商品行蹤 🔥

下面步驟照著來ᕦ(｀А´)ᕤ

1️⃣  輸入商品編號６碼，我會告訴您該商品的最新價格💰
例如：標籤上顯示331-446919，輸入後六碼即可！

2️⃣  若想持續追蹤此商品的價格動向，可點擊「追蹤此商品」，小偵探會在商品降價時第一時間通知您唷 🦐

3️⃣  如果想取消追蹤此商品🥲，可在訊息欄輸入「我的追蹤清單」，並點選「取消追蹤此商品」即可😭

4️⃣  由於系統的限制，目前追蹤清單的上限為12筆，如果超過則無法成功追蹤新的商品，所以～記得要定期清理已經不需要的商品唷🫡

醬子，大家有懂了嗎～🥺
跟著小偵探UNIQLO買起來⚡️
＼＼\\٩( 'ω' )و //／／"""
        )
    else:
        reply_message = TextSendMessage(
            text="汪汪！ 不知道你在說什麼耶～"
        )
    line_bot_api.reply_message(event.reply_token, reply_message)


if __name__ == "__main__":
    app.run()
