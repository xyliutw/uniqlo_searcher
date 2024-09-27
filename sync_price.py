from app.model.uniqlo_model import UniqloModel
import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

    
def get_official_site_data(message):
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
        time.sleep(1)
        step = 'Begin'
        product_id = product['product_id']
        print(f"==== {product_id} ====")
        print("--- GET SITE DATA ---")
        step = 'Get Site Data'
        product_data_website = get_official_site_data(product_id)
        if product_data_website:
            print("--- GET DB DATA ---")
            step = 'Get DB Data'
            price = int(float(product_data_website['productList'][0]['prices'][0]))
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
