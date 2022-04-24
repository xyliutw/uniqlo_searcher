from dotenv import load_dotenv
load_dotenv()

def refactor_default_flex_message(template, info, unsubscribe):
    template['hero']['url'] = info['main_pic']
    template['hero']['action']['uri'] = info['official_link']

    template['body']['contents'][0]['text'] = info['name']

    template['body']['contents'][1]['contents'][0]['contents'][1]['text'] = f"NT${info['price']}"
    template['body']['contents'][1]['contents'][1]['contents'][1]['text'] = f"NT${info['min_price']}"
    template['body']['contents'][1]['contents'][2]['contents'][1]['text'] = f"NT${info['origin_price']}"

    template['footer']['contents'][0]['action']['uri'] = info['official_link']
    if(not unsubscribe):
        template['footer']['contents'][1]['action']['uri'] = info['subscription_url']
    else:
        template['footer']['contents'][1]['action']['label'] = '取消追蹤此商品'
        template['footer']['contents'][1]['action']['uri'] = info['unsubscribe_url']

    if info['price'] == info['origin_price']:
        template['body']['contents'][1]['contents'][0]['contents'][1]['color'] = '#696969'
        template['body']['contents'][1]['contents'][0]['contents'][0]['color'] = '#696969'
    return template
