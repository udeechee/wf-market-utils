import datetime
import json
import tempfile
import logging
import re
import datetime as dt

#
# author: udeechee
#
import wfm_requests_impl as  wfm


relic_names = ["lith", "meso", "neo" "axi", "requiem"]
relic_desc = ["intact", "exceptional", "flawless", "radiant"]

def init_impl_logger(logging_level: int):
    logging.basicConfig(level=logging_level)

####################################
###### Implementation Methods ######
####################################

def margin_check_impl(item_name:str, max_rank:bool, offline_allowed:bool, international_allowed:bool):
    margin_check_dict = {}

    is_a_mod = False

    # Call WFM
    order_json = wfm.request_item_orders( item_name )
    stat_json = wfm.request_item_statistics(item_name)

    if "mod_rank" in order_json["payload"]["orders"][0]:
        is_a_mod = True


    min_sell:int = 10000
    max_buy:int = 0

    min_seller_names:list = []
    max_buyer_names:list = []
    ingame_name:str

    # Order Check
    for order in order_json["payload"]["orders"]:
        ingame_name = order["user"]["ingame_name"]
        # Offline Check
        if (not offline_allowed) and order["user"]["status"] == "offline":
            continue
        # Mod Check
        if is_a_mod:
            if max_rank:
                if order["mod_rank"] == 0:
                    continue
            else:
                if order["mod_rank"] != 0:
                    continue
        # International Check
        if (not international_allowed) and order["region"] != "en":
            continue
        # sell order
        if order["order_type"] == "sell":
            if order["platinum"] < min_sell:
                min_sell = order["platinum"]
                min_seller_names = [ingame_name]
            elif order["platinum"] == min_sell:
                min_seller_names += [ingame_name]
        # buy order
        if order["order_type"] == "buy":
            if order["platinum"] > max_buy:
                max_buy = order["platinum"]
                max_buyer_names = [ingame_name]
            elif order["platinum"] == max_buy:
                max_buyer_names += [ingame_name]


    margin_check_dict["Sellers"] = [min_seller_names, min_sell]
    margin_check_dict["Buyers"] = [max_buyer_names, max_buy]

    # print("\n")
    # print(margin_check_dict)
    # print("\n")

    return margin_check_dict


def cache_init_impl():
    wfm_item_list = wfm.request_all_items()["payload"]["items"]

    total_output = {}
    blueprint_cache = {}

    i = 0
    for item_json in wfm_item_list:
        url_name = item_json["url_name"]

        # Add custom filters here to drastically reduce time required
        if "prime" not in url_name:
            continue

        # For quicker testing
        # if i > 10:
        #     break
        # else:
        #     i += 1


        print ("---" + url_name + "---")

        stats_payload = wfm.request_item_statistics(url_name)
        stats = stats_payload["payload"]

        if len(stats["statistics_closed"]["48hours"])==0:
            continue

        is_a_mod = False
        if "mod_rank" in stats["statistics_closed"]["48hours"][0]:
            is_a_mod = True
        # if its a mod always use the 0 rank

    # tried to use time to take an average of the medians
        # t = dt.datetime.now()
        # Rounded to the hour
        # t = t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
        # tMinus1 = t - datetime.timedelta(hours=1)
        # tMinus2 = t - datetime.timedelta(hours=2)
        # tMinus3 = t - datetime.timedelta(hours=3)
        # statistics_closed = stats["statistics_closed"]["48hours"]
        # if statistics_closed[statistics_closed - 1] == t:
        #     # item was traded in the last hour
        #     median_plat = statistics_closed[statistics_closed - 1]["median"]

        # if a time is missing that means it had 0 volume

        statistics_closed_array = stats["statistics_closed"]["48hours"]

        if len(statistics_closed_array) >= 3:
            num_stats_used = 3
        else:
            num_stats_used = len(statistics_closed_array)

        most_recent_medians = []
        if is_a_mod:
            for i in range(len(statistics_closed_array)-1, 0):
                if len(most_recent_medians) == num_stats_used:
                    break
                if statistics_closed_array[i]["mod_rank"] != 0:
                    continue
                else:
                    most_recent_medians += [statistics_closed_array[i]["median"]]
        else:
            most_recent_medians = [statistics_closed_array[-1 * i]["median"] for i in range(1, num_stats_used+1)]

        if len(most_recent_medians) != 0:
            average_median_price = sum(most_recent_medians) / len(most_recent_medians)
        else:
            average_median_price = 0

        if average_median_price > 10 and average_median_price < 200:
            blueprint_cache[url_name] = {"avg_plat": average_median_price}
            print(url_name + " - " + str(average_median_price))

        # Orders for buy/sell, not necessarily fulfilled
        # statistics_live = stats["statistics_live"]

    # Combine jsons
    total_output["blueprints"] = blueprint_cache

    # file write
    output_file = "market-utils/wfm.cache"
    # output_string = ''.join('{}\t{}\n'.format(key, val) for key, val in blueprint_cache.items())
    output_string = json.dumps(total_output, indent=2)


    try:
        file = open(output_file, "w")
        file.write(output_string)
        file.flush()
        print("Wrote output to '" + file.name + "'")
        file.close()
    except IOError:
        print("Failed to write output to external file '" + output_file + "'")


def get_recent_orders():
    for i in range(0,10):
        print(wfm.request_recent_orders())


def find_newest_orders(wfmu_cache:dict, previous_buy_id:str, previous_sell_id:str):

    # Example layout of buy_results dict:
    # { "mesa_prime_set": [{"platinum": 50, "user": "bluoo"},{"platinum": 90, "user": "jakfk"}], "other_item": [...] }
    buy_results = {}
    sell_results = {}

    payload = wfm.request_recent_orders()["payload"]

    newest_buy_orders = filter_recent_orders(previous_buy_id, payload["buy_orders"])
    newest_sell_orders = filter_recent_orders(previous_sell_id, payload["sell_orders"])

    new_last_buy_id:str
    new_last_sell_id:str

    if newest_buy_orders:
        new_last_buy_id = newest_buy_orders[0]["id"]
    else:
        new_last_buy_id = previous_buy_id

    if newest_sell_orders:
        new_last_sell_id = newest_sell_orders[0]["id"]
    else:
        new_last_sell_id = previous_sell_id

    for buy_order in newest_buy_orders:
        url_name = buy_order["item"]["url_name"]
        if url_name not in wfmu_cache.keys():
            continue

        plat = buy_order["platinum"]
        user = buy_order["user"]["ingame_name"]

        order_info = {"platinum": plat, "user": user}

        if url_name in buy_results.keys():
            buy_results[url_name].append(order_info)
        else:
            buy_results[url_name] = [order_info]

    for sell_order in newest_sell_orders:
        url_name = sell_order["item"]["url_name"]
        if url_name not in wfmu_cache.keys():
            continue

        plat = sell_order["platinum"]
        user = sell_order["user"]["ingame_name"]

        order_info = {"platinum": plat, "user": user}

        if url_name in sell_results.keys():
            sell_results[url_name].append(order_info)
        else:
            sell_results[url_name] = [order_info]

    return {"buy_results": buy_results, "sell_results": sell_results, "last_buy_id": new_last_buy_id, "last_sell_id": new_last_sell_id}


def filter_recent_orders(last_known_id: str, order_list:list):
    if last_known_id == "0":
        return order_list

    i = 0
    for order in order_list:
        if order["id"] == last_known_id:
            return order_list[:i]
        i += 1
    return order_list



