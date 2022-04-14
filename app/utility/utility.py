def refactor_default_flex_message(template, info):
    template['hero']['url'] = info['main_pic']
    template['hero']['action']['uri'] = info['official_link']

    template['body']['contents'][0]['text'] = info['name']

    template['body']['contents'][1]['contents'][0]['contents'][1]['text'] = f"NT${info['price']}"
    template['body']['contents'][1]['contents'][1]['contents'][1]['text'] = f"NT${info['min_price']}"
    template['body']['contents'][1]['contents'][2]['contents'][1]['text'] = f"NT${info['origin_price']}"

    template['footer']['contents'][0]['action']['uri'] = info['official_link']
    template['footer']['contents'][1]['action']['uri'] = info['official_link']

    return template
