from app.model.uniqlo_model import UniqloModel
import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

    
def get_official_site_data(message):
    search_url = os.getenv('UNIQLO_SEARCH_URL_INSIDE')
    data = {
        "url": f"{search_url}{message}",
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

def send_notify(message):
    headers = {
        "Authorization": "Bearer " + os.getenv("LINE_NOTIFY"), 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': message }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code
        

uniqlo_model = UniqloModel()
products = uniqlo_model.get_product_list()

send_notify('\n開始更新')
time_start = time.time()
for product in products:
    try:
        step = 'Begin'
        product_id = product['product_id']
        print(f"==== {product_id} ====")
        print("--- GET SITE DATA ---")
        step = 'Get Site Data'
        product_data_website = get_official_site_data(product_id)
        if product_data_website:
            print("--- GET DB DATA ---")
            step = 'Get DB Data'
            price = int(float(product_data_website['prices'][0]))
            min_price_db = product['min_price']
            min_price = min_price_db if min_price_db < price else price
            print("--- UPDATE DB ---")
            step = 'Update DB'
            uniqlo_model.daily_update(product_id=product_id, price=price, min_price=min_price)
    except Exception as e:
        send_notify(f"\n更新發生錯誤\nStep:{step}\nErrorMsg:{str(e)}\nproduct_id:{product_id}")
time_end = time.time()

time_c= time_end - time_start
send_notify(f"\n同步成功！\n========\n共花費: {round(time_c)} sec\n更新:{len(products)}筆資料")
