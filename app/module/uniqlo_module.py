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

        info = {
            "origin_price": int(float(res['originPrice'])),
            "price": int(float(res['prices'][0])),
            "min_price": int(float(res['minPrice'])),
            "max_price": int(float(res['maxPrice'])),
            "name": res['name'],
            "product_code": res['productCode'],
            "main_pic": f"{os.getenv('UNIQLO_IMAGE_BASE')}{res['mainPic']}",
            "product_name": res['productName'],
            "official_link": f"{os.getenv('UNIQLO_OFFICIAL_BASE')}{res['productCode']}"
        }

        user_id = self.user_id

        template = json.load(
        open("app/template/default_flex.json", "r", encoding="utf-8")
        )
        flexMessage = refactor_default_flex_message(
            template, info
        )
        reply_message = FlexSendMessage(info['name'], flexMessage)
        return reply_message
