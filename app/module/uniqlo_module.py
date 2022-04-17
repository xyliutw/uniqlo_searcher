from app.model.uniqlo_model import UniqloModel
from linebot.models import (
    TextSendMessage,
    FlexSendMessage,
)
from ..utility.utility import refactor_default_flex_message
import os
import requests
import json
import psycopg2
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

class UniqloModule:
    def __init__(self, user_id = None, message = None):
        self.user_id = user_id
        self.message = message

    def get_current_price(self):
        name, flexMessage = self.get_product_price_from_website()
        if name == 0 and flexMessage == 0:
            reply_message = TextSendMessage(text="查無此商品")
            return reply_message
        else:
            reply_message = FlexSendMessage(name, flexMessage)
            return reply_message

    def get_product_price_from_website(self, user_id = None, product_id = None, unsubscribe = False):
        message = product_id if product_id is not None else self.message
        user_id = user_id if user_id is not None else self.user_id

        data = {
            "url": f"{os.getenv('UNIQLO_SEARCH_URL_INSIDE')}{message}",
            "pageInfo": {
                "page": 1,
                "pageSize": 24,
                "withSideBar": "Y"
            },
            "belongTo": "pc",
            "rank": "overall",
            "priceRange": {
                "low": 0,
                "high": 0
            },
            "color": [],
            "size": [],
            "season": [],
            "material": [],
            "sex": [],
            "identity": [],
            "insiteDescription": "",
            "exist": [],
            "searchFlag": True,
            "description": f"{message}"
        }
        header = {
            os.getenv('HEADER_1_K'): os.getenv('HEADER_1_V'),
            os.getenv('HEADER_2_K'): os.getenv('HEADER_2_V')
        } 
        r = requests.post(os.getenv('UNIQLO_SEARCH_URL'), headers=header, json=data)

        res = json.loads(r.text)

        if(res['resp'][2]['productSum'] == 0):
            return 0, 0

        res = res['resp'][1][0]

        info = {
            "origin_price": int(float(res['originPrice'])),
            "price": int(float(res['prices'][0])),
            "min_price": int(float(res['minPrice'])),
            "max_price": int(float(res['maxPrice'])),
            "name": res['name'],
            "product_code": res['productCode'],
            "main_pic": f"{os.getenv('UNIQLO_IMAGE_BASE')}{res['mainPic']}",
            "product_name": res['productName'],
            "official_link": f"{os.getenv('UNIQLO_OFFICIAL_BASE')}{res['productCode']}",
            "subscription_url": f"{os.getenv('SUBSCRIPTION_URL')}?uid={user_id}&product_id={message}",
            "unsubscribe_url": f"{os.getenv('UNSUBSCRIBE_URL')}?uid={user_id}&product_id={message}"
        }

        template = json.load(
        open("app/template/default_flex.json", "r", encoding="utf-8")
        )
        flexMessage = refactor_default_flex_message(
            template, info, unsubscribe
        )
        return info['name'], flexMessage

    def subscribe(self, data):
        if(data.get('uid') is None or data.get('product_id') is None):
            return "訂閱功能發生錯誤，請聯絡管理員"

        try:
            uniqlo_model = UniqloModel()
            uniqlo_model.add_subscription(data.get('uid'), data.get('product_id'))
        except psycopg2.errors.UniqueViolation:
            return "此商品您已訂閱"
        except Exception as e:
            print(e)
            return "訂閱功能發生錯誤，請聯絡管理員"
        return "訂閱成功👍"
    
    def unsubscribe(self, data):
        if(data.get('uid') is None or data.get('product_id') is None):
            return "訂閱功能發生錯誤，請聯絡管理員"

        try:
            uniqlo_model = UniqloModel()
            uniqlo_model.remove_subscription(data.get('uid'), data.get('product_id'))
        except Exception as e:
            print(e)
            return "訂閱功能發生錯誤，請聯絡管理員"
        return "取消訂閱成功👍"
    
    def send_notification(self):
        uniqlo_model = UniqloModel()
        user_list = uniqlo_model.get_send_list()

        send_candidate = defaultdict(list)
        for user_info in user_list:
            name, flex_message = self.get_product_price_from_website(user_info[1], user_info[2] , unsubscribe=True)
            send_candidate[user_info[1]].append(flex_message)

        for user_id, flex_messages in send_candidate.items():
            # send message here
            data = self.build_request_body(user_id, flex_messages)
            self.line_push(data)

        reply_message = TextSendMessage(text="發送完成")
        return reply_message
    
    def build_request_body(self, user_id, flex_messages):
        data = {
            "to": user_id,
            "messages": [
            {
                "type": "flex",
                "altText": "訂閱清單",
                "contents": {
                    "type": "carousel",
                    "contents": flex_messages
                }
            }
            ]
        }
        return data
    
    def line_push(self, data):
        header = {
            os.getenv('LINE_HEADER_K'): os.getenv('LINE_HEADER_V')
        } 
        r = requests.post(os.getenv('LINE_PUSH_URL'), headers=header, json=data)

        res = json.loads(r.text)

        return res
    
    def get_subscription_list(self):
        uniqlo_model = UniqloModel()
        user_list = uniqlo_model.get_user_subscription_list(self.user_id)

        if len(user_list) == 0:
            reply_message = TextSendMessage(text="查無訂閱清單")
            return reply_message

        items = []
        for user_info in user_list:
            name, flex_message = self.get_product_price_from_website(user_info[1], user_info[2], unsubscribe=True)
            items.append(flex_message)

        flexMessage = self.build_subscription_flex_message(items)
        reply_message = FlexSendMessage('訂閱清單', flexMessage)
        return reply_message

    def build_subscription_flex_message(self, items):
        template = {
            "type": "carousel",
            "contents": items
        }
        return template