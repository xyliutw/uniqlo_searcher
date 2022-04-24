from app.model.uniqlo_model import UniqloModel
from linebot.models import (
    TextSendMessage,
    FlexSendMessage,
)
from ..utility.utility import refactor_default_flex_message
import os
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
from collections import defaultdict
from dotenv import load_dotenv
import time
from urllib import parse

load_dotenv()

class UniqloModule:
    def __init__(self, user_id = None, message = None):
        self.user_id = user_id
        self.message = message

    def get_current_price(self):
        info, flexMessage = self.get_price()
        if info == 0:
            reply_message = TextSendMessage(text="查無此商品")
            return reply_message
        else:
            name = info['name']
            reply_message = FlexSendMessage(name, flexMessage)
            return reply_message

    def get_price(self, user_id = None, product_id = None, unsubscribe = False):
        message = product_id if product_id is not None else self.message
        user_id = user_id if user_id is not None else self.user_id

        uniqlo_model = UniqloModel()

        product_info = uniqlo_model.check_product_exist(message)

        if(len(product_info) != 0):
            product_id = message
            product_code = product_info[1]
            info = {
                "origin_price": product_info[3],
                "price": product_info[4],
                "min_price": product_info[5],
                "max_price": product_info[3],
                "name": product_info[6],
                "product_code": product_info[1],
                "main_pic": product_info[2],
                "product_name": product_info[7],
                "official_link": f"{os.getenv('UNIQLO_OFFICIAL_BASE')}{product_code}",
                "subscription_url": f"{os.getenv('SUBSCRIPTION_URL')}?uid={user_id}&product_id={product_id}",
                "unsubscribe_url": f"{os.getenv('UNSUBSCRIBE_URL')}?uid={user_id}&product_id={product_id}",
                "product_id": message,
                "last_notify_price": product_info[8],
            }
        else:
            res = self.get_official_site_data(message)
            if res == 0:
                return 0, 0

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
                "unsubscribe_url": f"{os.getenv('UNSUBSCRIBE_URL')}?uid={user_id}&product_id={message}",
                "product_id": message,
                "last_notify_price": None
            }
            low_price = self.get_product_low_price(info['product_code'])
            if low_price is not None:
                low_price = int(float(low_price))
            
                if( low_price < int(info['min_price'])):
                    info['min_price'] = low_price

            
            uniqlo_model.add_product_data(info) 

        template = json.load(
        open("app/template/default_flex.json", "r", encoding="utf-8")
        )
        flexMessage = refactor_default_flex_message(
            template, info, unsubscribe
        )

        return info, flexMessage

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
    
    def subscribe_v2(self, data):
        params = parse.parse_qs(parse.urlparse(data.get('liff.state')).query)
        if(params.get('uid') is None or params.get('product_id') is None):
            return "訂閱功能發生錯誤，請聯絡管理員"
        try:
            uniqlo_model = UniqloModel()
            uniqlo_model.add_subscription(params.get('uid')[0], params.get('product_id')[0])
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
    
    def send_notification(self, user_id):
        if user_id != os.getenv('ADMIN_UID'):
            reply_message = TextSendMessage(text="Unknown command, please contact ericlynn0912@gmail.com to get more information.")
            return reply_message
        uniqlo_model = UniqloModel()
        user_list = uniqlo_model.get_send_list()

        send_candidate = defaultdict(list)
        uniqlo_model = UniqloModel()
        for user_info in user_list:
            info, flex_message = self.get_price(user_info[1], user_info[2] , unsubscribe=True)
            if (info['last_notify_price'] is None or info['price'] < info['last_notify_price']) and info['price'] < info['origin_price']:
                send_candidate[user_info[1]].append(flex_message)
                try:
                    uniqlo_model.update_last_notify_price(info['product_id'], info['price'])
                except Exception:
                    reply_message = TextSendMessage(text="更新價格時發生錯誤")
                    return reply_message

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
            info, flex_message = self.get_price(user_info[1], user_info[2], unsubscribe=True)
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
    
    def get_product_low_price(self, product_code):
        try:
            response = requests.get(f"{os.getenv('UNIQLO_HISTORY_URL')}{product_code}")
            soup = BeautifulSoup(response.text, "html.parser")
            res = json.loads(soup.find_all(os.getenv('DATA_PART'))[int(os.getenv('DATA_INDEX'))].text)
            min_price = res[os.getenv('HISTORY_KEY')][os.getenv('LOW_PRICE')]
            return min_price
        except json.decoder.JSONDecodeError as e:
            return None
        except Exception as ex:
            return None
    
    def get_official_site_data(self, message):
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
            return 0
        res = res['resp'][1][0]

        return res
        
    def update_product_price(self, user_id):
        if user_id != os.getenv('ADMIN_UID'):
            reply_message = TextSendMessage(text="Unknown command, please contact ericlynn0912@gmail.com to get more information.")
            return reply_message

        uniqlo_model = UniqloModel()
        products = uniqlo_model.get_product_list()

        try:
            for product in products:
                product_id = product[0]
                product_data_website = self.get_official_site_data(product_id)
                product_date_in_db = uniqlo_model.check_product_exist(product_id)
                price = int(float(product_data_website['prices'][0]))
                min_price_db = product_date_in_db[5]
                min_price = min_price_db if min_price_db < price else price
                uniqlo_model.daily_update(product_id=product_id, price=price, min_price=min_price)
                time.sleep(2)
        except Exception:
            reply_message = TextSendMessage(text="[注意] 更新過程發生問題")
            return reply_message
        reply_message = TextSendMessage(text="更新完成")
        return reply_message