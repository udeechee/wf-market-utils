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

PLATINUM = "platinum"

RECENT_ORDERS = "recent_orders"
LAST_BUY_ID = "last_buy_id"
LAST_SELL_ID = "last_sell_id"

INPUT_FILE = "market-utils/wfm.cache"
PERCENT_THRESHOLD = 0.10

MEM_CACHE = {
    LAST_BUY_ID: "0",
    LAST_SELL_ID: "0"
}

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
        newest_order_results = impl.find_newest_orders(item_price_dict,
                                       previous_buy_id=MEM_CACHE[LAST_BUY_ID],
                                       previous_sell_id=MEM_CACHE[LAST_SELL_ID])

        buy_results = newest_order_results["buy_results"]
        sell_results = newest_order_results["sell_results"]

        MEM_CACHE[LAST_BUY_ID] = newest_order_results[LAST_BUY_ID]
        MEM_CACHE[LAST_SELL_ID] = newest_order_results[LAST_SELL_ID]

        for item, info_list in buy_results.items():
            # avg/current price
            price = item_price_dict[item]

            names: list = []

            for info in info_list:
                recent_price = info[PLATINUM]
                user = info["user"]
                perc_diff = round(percent_diff(price, recent_price), 4)

                output_string:str = ""
                if perc_diff < -PERCENT_THRESHOLD:
                    output_string += "BUYER UP " + str(perc_diff*100) + "% - " + str(user) + ": " + str(recent_price) + "\n"

                if output_string:
                    output_string = item + " - " + str(price) + "\n" + output_string
                    print(output_string)

        for item, info_list in sell_results.items():
            # avg/current price
            price = item_price_dict[item]

            names: list = []

            for info in info_list:
                recent_price = info[PLATINUM]
                user = info["user"]
                perc_diff = round(percent_diff(price, recent_price), 4)

                output_string: str = ""
                if perc_diff > PERCENT_THRESHOLD:
                    output_string += "SELLER DOWN " + str(perc_diff * 100) + "% - " + str(user) + ": " + str(
                        recent_price) + "\n"

                if output_string:
                    output_string = item + " - " + str(price) + "\n" + output_string
                    print(output_string)

        time.sleep(10.0)

#          Gotta fix how the last_id works, so its updated at least in memory

except KeyboardInterrupt:
    print("Exiting")
    raise SystemExit


