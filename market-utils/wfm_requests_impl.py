import time

import requests

WARFRAME_MARKET_ROOT = "https://api.warframe.market/v1/"
ITEMS_REQUEST = "items"
STATISTICS_REQUEST = "statistics"
ORDERS_REQUEST = "orders"
MOST_RECENT = "most_recent"

# def start_session():
# Start session
session = requests.Session()
session.headers.update({"Platform": "pc", "Language": "en"})


def __build_url_request_items():
    return WARFRAME_MARKET_ROOT + ITEMS_REQUEST


def __build_url_request_item(url_name: str):
    return __build_url_request_items() + "/" + url_name


def __build_url_request_item_statistics(url_name: str):
    return __build_url_request_item(url_name) + "/" + STATISTICS_REQUEST


def __build_url_request_item_orders(url_name: str):
    return __build_url_request_item(url_name) + "/" + ORDERS_REQUEST


def __build_url_request_recent_orders():
    return WARFRAME_MARKET_ROOT + MOST_RECENT


def delay_request(f):
    def wrapper_delay(*args, **kwargs) -> dict:
        def get_json(uri: str):
            return session.get(uri).json()

        time.sleep(0.37)
        return get_json(f(*args, **kwargs))

    return wrapper_delay


@delay_request
def request_all_items():
    return __build_url_request_items()


@delay_request
def request_item(url_name: str):
    return __build_url_request_item(url_name)


@delay_request
def request_item_orders(url_name: str):
    return __build_url_request_item_orders(url_name)


@delay_request
def request_item_statistics(url_name: str):
    return __build_url_request_item_statistics(url_name)


@delay_request
def request_recent_orders():
    return __build_url_request_recent_orders()
