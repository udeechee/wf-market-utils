# Order Watcher

# Not sure how this and vigilant will interface together, but both are useful and do a separate task.
# Right now just took vig and copied it here to work on the meat of order_watcher, but at somepoint they'll need to be combined
# and they will need to write / read to same file.

# This script watches the recent orders and checks prices of items (those in wfm.cache) to see if they are flippable
# This script is setup and then runs in the background, making calls to the cli as needed.


# Assuming wfm.cache is already populated?
import json
import wfm_requests_impl as wfm
import cli
import impl
import time

BLUEPRINTS = "blueprints"
MODS = "mods"
AVG_PLAT = "avg_plat"

RECENT_ORDERS = "recent_orders"
LAST_BUY_ID = "last_buy_id"
LAST_SELL_ID = "last_sell_id"

INPUT_FILE = "market-utils/wfm.cache"
PERCENT_THRESHOLD = 0.10

def parse_input_cache(input_file:str):
    recent_order_info = {}
    item_price_dict = {}

    f = open(input_file, "r")
    loaded:dict = json.load(f)

    if RECENT_ORDERS in loaded.keys():
        recent_order_info[LAST_BUY_ID] = loaded[RECENT_ORDERS][LAST_BUY_ID]
        recent_order_info[LAST_SELL_ID] = loaded[RECENT_ORDERS][LAST_SELL_ID]
    else:
        recent_order_info[LAST_BUY_ID] = "0"
        recent_order_info[LAST_SELL_ID] = "0"


    if BLUEPRINTS in loaded.keys():
        for (k, v) in loaded[BLUEPRINTS].items():
            item_price_dict[k] = v[AVG_PLAT]

    return {RECENT_ORDERS: recent_order_info, BLUEPRINTS: item_price_dict}

def percent_diff(orig: float, updated: float):
    return (orig - updated)/orig

try:
    parsed_cached = parse_input_cache(INPUT_FILE)
    i:int = 0

    item_price_dict = parsed_cached[BLUEPRINTS]
    recent_order_info = parsed_cached[RECENT_ORDERS]

    while True:
        impl.find_newest_orders(item_price_dict,
                                       previous_buy_id=recent_order_info[LAST_BUY_ID],
                                       previous_sell_id=recent_order_info[LAST_SELL_ID])

        for item, price in item_price_dict.items():
            margin_check_dict = cli.margin_check_impl(item, False, False, False)

            sell_names:list = margin_check_dict["Sellers"][0]
            buy_names:list = margin_check_dict["Buyers"][0]

            updated_sell:float = margin_check_dict["Sellers"][1]
            updated_buy:float = margin_check_dict["Buyers"][1]

            sell_perc = round(percent_diff(price, updated_sell), 4)
            buy_perc = round(percent_diff(price, updated_buy), 4)

            output_string:str = ""

            if sell_perc > PERCENT_THRESHOLD:
                output_string += "SELLER DOWN " + str(sell_perc*100) + "% - " + str(sell_names) + ": " + str(updated_sell) + "\n"

            if buy_perc < -PERCENT_THRESHOLD:
                output_string += "BUYER UP " + str(buy_perc*100) + "% - " + str(buy_names) + ": " + str(updated_buy) + "\n"

            if output_string:
                output_string = item + " - " + str(price) + "\n" + output_string
                print(output_string)

        time.sleep(60.0)

except KeyboardInterrupt:
    print("Exiting")
    raise SystemExit


