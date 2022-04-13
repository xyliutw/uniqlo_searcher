from linebot.models import (
    TextSendMessage,
    FlexSendMessage,
)
from ..utility.utility import refactor_default_flex_message
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

class UniqloModule:
    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message


    def get_current_price(self):
        data = {
            "url": f"{os.getenv('UNIQLO_SEARCH_URL_INSIDE')}{self.message}",
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
            "description": f"{self.message}"
        }
        header = {
            os.getenv('HEADER_1_K'): os.getenv('HEADER_1_V'),
            os.getenv('HEADER_2_K'): os.getenv('HEADER_2_V')
        } 
        r = requests.post(os.getenv('UNIQLO_SEARCH_URL'), headers=header, json=data)

        res = json.loads(r.text)['resp'][1][0]

        uniqlo_official_base = os.getenv['UNIQLO_OFFICIAL_BASE']
        info = {
            "origin_price": res['originPrice'],
            "prices": res['prices'],
            "min_price": res['minPrice'],
            "max_price": res['maxPrice'],
            "name": res['name'],
            "product_code": res['productCode'],
            "main_pic": res['mainPic'],
            "product_name": res['productName']
        }

        msg = f"""商品名稱: {info['name']}

商品原價:{info['origin_price']}
歷史最低:{info['min_price']}

• 當前價格: {info['prices'][0]}

(測試）當前使用者：{self.user_id}

參考: {uniqlo_official_base}{info['product_code']}"""
        reply_message = TextSendMessage(text=msg)
        return reply_message

        # template = json.load(
        # open("app/template/default_flex.json", "r", encoding="utf-8")
        # )
        # flexMessage = refactor_default_flex_message(
        #     template, sumDict, stock_name, stock_id
        # )
        # reply_message = FlexSendMessage(stock_id, flexMessage)
        # return reply_message
