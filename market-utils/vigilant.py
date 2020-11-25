# Vigilant

# Put all the peices together.
# (1) first runs the cache-and-filter which writes to a file
# (2) sets up pulling for those cached in the file
# (3) after cache updates, NicePriceWatcher and FlipFinder process for new finds

# This script is setup and then runs in the background, making calls to the cli as needed.

# Assuming wfm.cache is already populated?
import json
import wfm_requests_impl as wfm
import cli
import time

BLUEPRINTS = "blueprints"
MODS = "mods"
AVG_PLAT = "avg_plat"

INPUT_FILE = "market-utils/wfm.cache"
PERCENT_THRESHOLD = 0.10

def agg_items_to_check(input_file:str):
    # Agg of blueprints and mods
    item_price_dict = {}

    f = open(input_file, "r")
    loaded:dict = json.load(f)

    if BLUEPRINTS in loaded.keys():
        for (k, v) in loaded[BLUEPRINTS].items():
            item_price_dict[k] = v[AVG_PLAT]

    if MODS in loaded.keys():
        for (k, v) in loaded[MODS].items():
            item_price_dict[k] = v[AVG_PLAT]

    return item_price_dict

def percent_diff(orig: float, updated: float):
    return (orig - updated)/orig

try:
    item_price_dict = agg_items_to_check(INPUT_FILE)
    i:int = 0

    while True:
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


