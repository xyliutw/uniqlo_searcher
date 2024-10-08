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
import subprocess

load_dotenv()

class UniqloModule:
    def __init__(self, user_id = None, message = None):
        self.user_id = user_id
        self.message = message

    def get_current_price(self):
        info, flexMessage = self.get_price()
        if info == 0 or len(self.message) != 6:
            reply_message = TextSendMessage(text="很抱歉，查無此商品。 汪汪！")
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

        if(product_info is not None):
            product_id = message
            product_code = product_info['product_code']
            info = {
                "origin_price": product_info['origin_price'],
                "price": product_info['price'],
                "min_price": product_info['min_price'],
                "max_price": product_info['origin_price'],
                "name": product_info['name'],
                "product_code": product_info['product_code'],
                "main_pic": product_info['image_url'],
                "product_name": product_info['product_name'],
                "official_link": f"{os.getenv('UNIQLO_OFFICIAL_BASE')}{product_code}",
                "subscription_url": f"{os.getenv('SUBSCRIPTION_URL')}?uid={user_id}&product_id={product_id}",
                "unsubscribe_url": f"{os.getenv('UNSUBSCRIBE_URL')}?uid={user_id}&product_id={product_id}",
                "product_id": message,
                "last_notify_price": product_info['last_notify_price'],
            }
        else:
            res = self.get_official_site_data(message)
            if res is None:
                return 0, 0
            if type(res) == dict:
                res = res['productList'][0]
                info = {
                    "origin_price": int(float(res['originPrice'])),
                    "price": int(float(res['prices'][0])),
                    "min_price": int(float(res['minPrice'])),
                    "max_price": int(float(res['originPrice'])),
                    "name": res['name'],
                    "product_code": res['productCode'],
                    "main_pic": f"{os.getenv('UNIQLO_IMAGE_BASE')}{res['mainPic']}",
                    "product_name": res['productName'],
                    "official_link": f"{os.getenv('UNIQLO_OFFICIAL_BASE')}{res['productCode']}",
                    "subscription_url": f"{os.getenv('SUBSCRIPTION_URL')}?uid={user_id}&product_id={message}",
                    "unsubscribe_url": f"{os.getenv('UNSUBSCRIBE_URL')}?uid={user_id}&product_id={message}",
                    "product_id": message,
                    "last_notify_price": int(float(res['prices'][0]))
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
            return "追蹤功能發生錯誤，請聯絡管理員"

        try:
            uniqlo_model = UniqloModel()
            uniqlo_model.add_subscription(data.get('uid'), data.get('product_id'))
        except psycopg2.errors.UniqueViolation:
            return "此商品您已追蹤"
        except Exception as e:
            print(e)
            return "追蹤功能發生錯誤，請聯絡管理員"
        return "追蹤成功👍"
    
    def subscribe_v2(self, data):
        params = parse.parse_qs(parse.urlparse(data.get('liff.state')).query)
        if(params.get('uid') is None or params.get('product_id') is None):
            self.send_notify('uid or product_id is none.')
            return "追蹤功能發生錯誤，請聯絡管理員"
        try:
            uniqlo_model = UniqloModel()
            subscription_amount = uniqlo_model.get_user_subscription_amount(params.get('uid')[0])
            if subscription_amount is not None and subscription_amount['total'] >= 12:
                return "追蹤功能上限為12筆商品，請移除後重試"
            uniqlo_model.add_subscription(params.get('uid')[0], params.get('product_id')[0])
        except psycopg2.errors.UniqueViolation:
            return "此商品您已追蹤"
        except Exception as e:
            print(e)
            self.send_notify(str(e))
            self.send_notify(f"{params.get('uid')}, {subscription_amount}, {params.get('product_id')}")
            return "追蹤功能發生錯誤，請聯絡管理員"
        return "追蹤成功👍"
    
    def unsubscribe(self, data):
        if(data.get('uid') is None or data.get('product_id') is None):
            return "追蹤功能發生錯誤，請聯絡管理員"

        try:
            uniqlo_model = UniqloModel()
            uniqlo_model.remove_subscription(data.get('uid'), data.get('product_id'))
        except Exception as e:
            print(e)
            return "追蹤功能發生錯誤，請聯絡管理員"
        return "取消追蹤成功👍"
    
    def unsubscribe_v2(self, data):
        params = parse.parse_qs(parse.urlparse(data.get('liff.state')).query)
        if(params.get('uid') is None or params.get('product_id') is None):
            self.send_notify('uid or product_id is none.')
            return "追蹤功能發生錯誤，請聯絡管理員"

        try:
            uniqlo_model = UniqloModel()
            uniqlo_model.remove_subscription(params.get('uid')[0], params.get('product_id')[0])
        except Exception as e:
            print(e)
            self.send_notify(str(e))
            return "追蹤功能發生錯誤，請聯絡管理員"
        return "取消追蹤成功👍"
    
    def send_notify(self, message):
        headers = {
            "Authorization": "Bearer " + os.getenv("LINE_NOTIFY"), 
            "Content-Type" : "application/x-www-form-urlencoded"
        }

        payload = {'message': message }
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        return r.status_code

    def cron_setter(self, user_id):
        if user_id != os.getenv('ADMIN_UID'):
            reply_message = TextSendMessage(text="Unknown command, please contact ericlynn0912@gmail.com to get more information.")
            return reply_message
        try:
            subprocess.run(["crontab", "/app/crontab"])
            subprocess.run(["crontab", "-l"])
            subprocess.run(["crond", "-d", "8"])
        except Exception as e:
            print(e)
            self.send_notify(str(e))
            return "Crontab failed."
        reply_message = TextSendMessage(text="Crontab is set.")
        return reply_message

    def send_notification(self, user_id):
        if user_id != os.getenv('ADMIN_UID'):
            reply_message = TextSendMessage(text="Unknown command, please contact ericlynn0912@gmail.com to get more information.")
            return reply_message
        uniqlo_model = UniqloModel()
        user_list = uniqlo_model.get_send_list()

        send_candidate = defaultdict(list)
        try:
            for user_info in user_list:
                info, flex_message = self.get_price(user_info['uid'], user_info['product_id'] , unsubscribe=True)
                if type(info) == int:
                    uniqlo_model.delete_invalid_product(user_info['product_id'])
                    continue
                if (info['last_notify_price'] is None or (info['price'] < info['last_notify_price'])) and info['price'] < info['origin_price']:
                    # self.send_notify(f"\[Enter Here]\nMsg:\n{info}")
                    send_candidate[user_info['uid']].append(flex_message)
                    try:
                        uniqlo_model.update_last_notify_price(info['product_id'], info['price'])
                    except Exception:
                        reply_message = TextSendMessage(text="更新價格時發生錯誤")
                        return reply_message
                elif info['last_notify_price'] is not None and info['price'] > info['last_notify_price']: # 特價已結束，重置last_notify_price以讓下次有特價會繼續發送通知
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
        except Exception as e:
            self.send_notify(f"\n發送特價通知時發生錯誤\nErrorMsg:{str(e)}\n{info}\nuid: {user_info['uid']}\nproduct_id: {user_info['product_id']}")
            reply_message = TextSendMessage(text="Error")
            return reply_message

    
    def build_request_body(self, user_id, flex_messages):
        data = {
            "to": user_id,
            "messages": [
            {
                "type": "flex",
                "altText": "追蹤清單",
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
            reply_message = TextSendMessage(text="查無追蹤清單")
            return reply_message

        items = []
        for user_info in user_list:
            info, flex_message = self.get_price(user_info['uid'], user_info['product_id'], unsubscribe=True)
            items.append(flex_message)

        flexMessage = self.build_subscription_flex_message(items)
        reply_message = FlexSendMessage('追蹤清單', flexMessage)
        return reply_message

    def build_subscription_flex_message(self, items):
        template = {
            "type": "carousel",
            "contents": items[:12]
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
            "url": f"/tw/zh_TW/search.html?description={message}",
            "pageInfo": {
                "page": 1,
                "pageSize": 24
            },
            "belongTo": "pc",
            "rank": "overall",
            "priceRange": {
                "low": 0,
                "high": 0
            },
            "color": [],
            "size": [],
            "identity": [],
            "exist": [],
            "searchFlag": True,
            "description": f"{message}",
            "stockFilter": "warehouse"
        }
        header = {
            os.getenv('HEADER_1_K'): os.getenv('HEADER_1_V'),
            os.getenv('HEADER_2_K'): os.getenv('HEADER_2_V')
        } 
        r = requests.post(os.getenv('UNIQLO_SEARCH_URL_NEW'), headers=header, json=data)

        # 檢查 API 回應是否成功
        if r.status_code != 200:
            print(f"Request failed with status code {r.status_code}")
            return None

        res = json.loads(r.text)

        # 確保回應格式正確並且有產品數據
        if 'resp' not in res:
            print("Response format is not as expected or missing productSum.")
            return None

        # 檢查產品總數
        product_sum = res['resp'][0].get('productSum', 0)
        if product_sum == 0:
            return None

        return res['resp'][0]

    def operate_db(self):
        try:
            uniqlo_model = UniqloModel()
            result = uniqlo_model.operate_db(self.message)
            reply_message = TextSendMessage(text=result)
        except Exception as e:
            print(e)
            self.send_notify(str(e))
            return "操作錯誤，請聯絡管理員"
        return reply_message