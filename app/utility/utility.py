def refactor_default_flex_message(template, stock_info, stock_name, stock_id):
    template["body"]["contents"][0]["text"] = f"{stock_name} ({stock_id})"

    template["body"]["contents"][2]["contents"][0]["contents"][1][
        "text"
    ] = f"{stock_info.get('max')}"
    template["body"]["contents"][2]["contents"][1]["contents"][1][
        "text"
    ] = f"{stock_info.get('min')}"

    if stock_info["new_diff"] < 0:
        template["body"]["contents"][2]["contents"][2]["contents"][1][
            "text"
        ] = f"{stock_info['new_close']}  {stock_info['new_diff']}({stock_info['new_diff_perc']}%)"
        template["body"]["contents"][2]["contents"][2]["contents"][1][
            "color"
        ] = "#00CC00"
    else:
        template["body"]["contents"][2]["contents"][2]["contents"][1][
            "text"
        ] = f"{stock_info['new_close']}  +{stock_info['new_diff']}({stock_info['new_diff_perc']}%)"
        template["body"]["contents"][2]["contents"][2]["contents"][1][
            "color"
        ] = "#CC0000"
    template["footer"]["contents"][0]["action"]["label"] = "Reference"
    template["footer"]["contents"][0]["action"][
        "uri"
    ] = f"https://tw.stock.yahoo.com/quote/{stock_id}/technical-analysis"

    return template
