import argparse
import logging

from impl import margin_check_impl, init_impl_logger, cache_init_impl


#
# author: udeechee
#
# Useful links:
# https://docs.google.com/document/d/1121cjBNN4BeZdMBGil6Qbuqse-sWpEXPpitQH5fb_Fo/edit#
# https://cwong8.github.io/projects/warframe_market/JSON_SQL/
# https://github.com/WFCD/market-api-spec/blob/master/openapi.yaml
# https://market-docs.warframestat.us/openapi.json
#
# Usage EX:
#   venv/bin/python3 market-utils/cli.py margin-check --item nezha_prime_blueprint
#
#

def parse_args(alt_args=None):
    """

    Explanation of parser structure:
      First defined is a "parent" parser which defines args that can be used by any of the operations (i.e. '--profile')
      Next defined is a "main" parser that serves as a way to organize our operations/subparsers.
          The "main" parser has four subparsers, one subparser for each operation
      Each subparser defines its own set of additional args (e.x. 'check-margin' op has unique arg '--item')
          and specifies it uses the "parent" parser for access to the parent args.

    Parameters
    ----------
    alt_args

    Returns
    -------

    """
    # Parent Parser
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--output-file', "--out",
                               help='File to log the output to.',
                               required=False)

    parent_parser.add_argument('--log-level',
                               type=str,
                               choices=["ERROR", "WARN", "INFO", "DEBUG"],
                               default="INFO",
                               help='The log level to use.')

    # Main Parser
    parser = argparse.ArgumentParser(description='Provides WF Market Utilities')

    # Subparsers
    subparsers = parser.add_subparsers(dest="op", help='sub-command help')

    # MarginCheck Subparser
    parser_mc = subparsers.add_parser('margin-check', help='"margin-check" operation. Retrieves the current lowest-seller and highest-buyer.', parents=[parent_parser])
    parser_mc.add_argument('--item', type=str, metavar="item", default=None, help="The item to margin-check path used for the query.")
    parser_mc.add_argument('--max-rank', "-M", default=False, action="store_true",
                           help="If the item is a mod, use the max-rank (otherwise use 0 rank).")
    parser_mc.add_argument('--offline-allowed', "-OA", default=False,action="store_true", help="Whether or not to include orders from offline players (default behavior does not include offline orders).")
    parser_mc.add_argument('--international', "-I", default=False, action="store_true",
                           help="Whether or not to include orders from people who may not speak english.")

    # Caching Subparser
        # Have different "levels" of caching (items and their prices/info) based on time intervals
        # maybe the "big" cache once a day, to narrow down a list of opportunity items
        # then the "smaller" cache keeps up to date on the current buy/sell
    parser_init_cache = subparsers.add_parser('init-cache',
                                      help='Creates caches of filtered data',
                                      parents=[parent_parser])
    # parser_init_cache.add_argument('--time', '-t',  type=valid_date, metavar="time", default="24h",
    #                        help="Times to consider", )

    parser_refresh_cache = subparsers.add_parser('refresh-cache',
                                              help='Refreshes cache',
                                              parents=[parent_parser])

    # IDEAS for future features:

    # NicePriceWatcher Subparser
    # Basically looks at new/incoming buy/sell offers. If it is above/below X percentage points from the median
    #   then ALERT. Caching will be useful here.

    # This is already sort of implemented using the init-cache and vigilant.py
    
    # Improvement would be to look at the most recently added orders and check those,
    #   that way its event driven rather than picking up the best orders once an iteration.

    # FlipFinder Subparser
    # Finds items (above a threshold of M minimum platinum) that have close buy/sell prices/ are bound by P plat.
    # |B - S| < P


    if alt_args:
        args = parser.parse_args(args=alt_args)
    else:
        args = parser.parse_args()

    return args


def margin_check_cli(args: argparse.Namespace):
    args_dict = vars(args)

    item = args_dict.get("item")
    max_rank = args_dict.get("max_rank")
    offline_allowed = args_dict.get("offline_allowed")
    international = args_dict.get("international")

    margin_check_dict = margin_check_impl(item, max_rank, offline_allowed, international)

    print("\n")
    print(margin_check_dict)
    print("\n")


def init_cache_cli(args: argparse.Namespace):
    args_dict = vars(args)

    min_plat = 5
    max_plat = 300

    cache_init_impl()

def refresh_cache_cli(args: argparse.Namespace):
    args_dict = vars(args)

def main():

    # Parse Args
    args = parse_args()

    # Logging
    log_level = args.log_level
    logging.basicConfig(level=logging.getLevelName(log_level))
    logging.info(f'Running {args.op} with args {args}')

    init_impl_logger(log_level)

    # calling functions depending on type of argument
    if args.op == 'margin-check':
        margin_check_cli(args)
    elif args.op == 'init-cache':
        init_cache_cli(args)
    elif args.op == 'refresh-cache':
        refresh_cache_cli(args)


if __name__ == '__main__':
    main()
