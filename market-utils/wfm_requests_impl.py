import time

import requests

WARFRAME_MARKET_ROOT = "https://api.warframe.market/v1/"
ITEMS_REQUEST = "items"
STATISTICS_REQUEST = "statistics"
ORDERS_REQUEST = "orders"

# def start_session():
# Start session
session = requests.Session()
session.headers.update({"Platform": "pc", "Language": "en"})


def build_url_request_items():
    return WARFRAME_MARKET_ROOT + ITEMS_REQUEST


def build_url_request_item(url_name: str):
    return build_url_request_items() + "/" + url_name


def build_url_request_item_statistics(url_name: str):
    return build_url_request_item(url_name) + "/" + STATISTICS_REQUEST


def build_url_request_item_orders(url_name: str):
    return build_url_request_item(url_name) + "/" + ORDERS_REQUEST


def request_all_items():
    return serve_request(build_url_request_items())


def request_item(url_name: str):
    return serve_request(build_url_request_item(url_name))


def request_item_orders(url_name: str):
    return serve_request(build_url_request_item_orders(url_name))


def request_item_statistics(url_name: str):
    return serve_request(build_url_request_item_statistics(url_name))


# Keeps requests per second less than 3
def serve_request(uri: str):
    time.sleep(0.37)
    return session.get(uri).json()
