import ujson as json
from unicorn_fy import UnicornFy
from run import app


class Binance_Websocket_Handler:
    @staticmethod
    def is_json(data):
        """
        Is the string in json format?

        :param data: the data to verify
        :type data: str

        :return: True or False
        :rtype: bool
        """
        try:
            json.loads(data)
        except ValueError:
            return False
        except TypeError:
            return False
        return True

    @staticmethod
    def set_to_false_if_not_exist(value, key):
        """
        some vars are non existent if they would be empty, so we create the missing vars with default values

        :param value: default value
        :type value: str

        :param key: the key name
        :type key: str

        :return: final value
        :rtype: str
        """
        try:
            if value[key]:
                return value[key]
        except KeyError:
            value[key] = False
            return value
        except IndexError:
            value[key] = False
            return value

    def binance_futures_websocket(BOT, stream_data_json, exchange="binance.com-futures", show_deprecated_warning=False):
        """
        unicorn_fy binance.com-futures raw_stream_data

        :param stream_data_json: The received raw stream data from the Binance websocket
        :type stream_data_json: json

        :param exchange: Exchange endpoint.
        :type exchange: str

        :param show_deprecated_warning: Show or hide warning
        :type show_deprecated_warning: bool

        :return: dict
        """
        unicorn_fied_data = False

        BOT.log.info("UnicornFy->binance_futures_websocket(" + str(stream_data_json) + ")")
        if show_deprecated_warning is True:
            pass
        if BOT.is_json(stream_data_json) is False:
            return stream_data_json

        stream_data = json.loads(stream_data_json)

        try:
            if stream_data['e'] == 'outboundAccountInfo':
                stream_data = {'data': stream_data}
            elif stream_data['e'] == 'executionReport':
                stream_data = {'data': stream_data}
            elif stream_data['e'] == 'balanceUpdate':
                stream_data = {'data': stream_data}
            elif stream_data['e'] == 'ORDER_TRADE_UPDATE':
                stream_data = {'data': stream_data}
            elif stream_data['e'] == 'ACCOUNT_UPDATE':
                stream_data = {'data': stream_data}
            elif stream_data['e'] == 'ACCOUNT_CONFIG_UPDATE':
                stream_data = {'data': stream_data}
            elif stream_data['e'] == 'MARGIN_CALL':
                stream_data = {'data': stream_data}
        except KeyError:
            pass
        try:
            if stream_data['stream'].find('@depth5') != -1:
                stream_data['data']['e'] = "depth"
                stream_data['data']['depth_level'] = 5
            elif stream_data['stream'].find('@depth10') != -1:
                stream_data['data']['e'] = "depth"
                stream_data['data']['depth_level'] = 10
            elif stream_data['stream'].find('@depth20') != -1:
                stream_data['data']['e'] = "depth"
                stream_data['data']['depth_level'] = 20
            elif "@bookTicker" in stream_data['stream']:
                stream_data['data']['e'] = "bookTicker"
        except KeyError:
            pass

        try:
            # return if already unicorn_fied
            if stream_data['unicorn_fied']:
                return stream_data
        except KeyError:
            pass

        try:
            if stream_data['result'] is None:
                BOT.log.debug(f"UnicornFy->binance_futures_websocket({str(stream_data)}, {str(exchange)}")
                return stream_data
            else:
                BOT.log.debug(f"UnicornFy->binance_futures_websocket({str(stream_data)}, {str(exchange)}")
                return stream_data
        except KeyError:
            pass

        try:
            if stream_data['error']:
                BOT.log.debug(f"UnicornFy->binance_futures_websocket({str(stream_data)}, {str(exchange)}")
                return stream_data
        except KeyError:
            pass

        try:
            if stream_data['data']['e'] == 'aggTrade':
                unicorn_fied_data = {'stream_type': stream_data['stream'],
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['s'],
                                     'aggregate_trade_id': stream_data['data']['a'],
                                     'price': stream_data['data']['p'],
                                     'quantity': stream_data['data']['q'],
                                     'first_trade_id': stream_data['data']['f'],
                                     'last_trade_id': stream_data['data']['l'],
                                     'trade_time': stream_data['data']['T'],
                                     'is_market_maker': stream_data['data']['m']}
            elif stream_data['data']['e'] == 'trade':
                # Todo: KeyError: 'b'
                # 'buyer_order_id': stream_data['data']['b'],
                # Todo: KeyError: 'a'
                # 'seller_order_id': stream_data['data']['a'],
                # Todo: KeyError: 'M'
                # , 'ignore': stream_data['data']['M']
                unicorn_fied_data = {'stream_type': stream_data['stream'],
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['s'],
                                     'trade_id': stream_data['data']['t'],
                                     'price': stream_data['data']['p'],
                                     'quantity': stream_data['data']['q'],
                                     'trade_time': stream_data['data']['T'],
                                     'is_market_maker': stream_data['data']['m']}
            elif stream_data['data']['e'] == 'kline':
                stream_data['data'] = BOT.set_to_false_if_not_exist(stream_data['data'], 'f')
                stream_data['data'] = BOT.set_to_false_if_not_exist(stream_data['data'], 'L')
                unicorn_fied_data = {'stream_type': stream_data['stream'],
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['s'],
                                     'kline': {'kline_start_time': stream_data['data']['k']['t'],
                                               'kline_close_time': stream_data['data']['k']['T'],
                                               'symbol': stream_data['data']['k']['s'],
                                               'interval': stream_data['data']['k']['i'],
                                               'first_trade_id': stream_data['data']['f'],
                                               'last_trade_id': stream_data['data']['L'],
                                               'open_price': stream_data['data']['k']['o'],
                                               'close_price': stream_data['data']['k']['c'],
                                               'high_price': stream_data['data']['k']['h'],
                                               'low_price': stream_data['data']['k']['l'],
                                               'base_volume': stream_data['data']['k']['v'],
                                               'number_of_trades': stream_data['data']['k']['n'],
                                               'is_closed': stream_data['data']['k']['x'],
                                               'quote': stream_data['data']['k']['q'],
                                               'taker_by_base_asset_volume': stream_data['data']['k']['V'],
                                               'taker_by_quote_asset_volume': stream_data['data']['k']['Q'],
                                               'ignore': stream_data['data']['k']['B']}}
            elif stream_data['data']['e'] == '24hrMiniTicker':
                try:
                    if stream_data['stream']:
                        pass
                except KeyError:
                    stream_data['stream'] = '!miniTicker@arr'
                unicorn_fied_data = {'stream_type': stream_data['stream'],
                                     'event_type': stream_data['data']['e'],
                                     'data': []}

                try:
                    for item in stream_data['items']:
                        data = {'stream_type': stream_data['stream'],
                                'event_type': item['e'],
                                'event_time': item['E'],
                                'symbol': item['s'],
                                'close_price': item['c'],
                                'open_price': item['o'],
                                'high_price': item['h'],
                                'low_price': item['l'],
                                'taker_by_base_asset_volume': item['v'],
                                'taker_by_quote_asset_volume': item['q']}
                        unicorn_fied_data['data'].append(data)
                except KeyError:
                    data = {'stream_type': stream_data['stream'],
                            'event_type': stream_data['data']['e'],
                            'event_time': stream_data['data']['E'],
                            'symbol': stream_data['data']['s'],
                            'close_price': stream_data['data']['c'],
                            'open_price': stream_data['data']['o'],
                            'high_price': stream_data['data']['h'],
                            'low_price': stream_data['data']['l'],
                            'taker_by_base_asset_volume': stream_data['data']['v'],
                            'taker_by_quote_asset_volume': stream_data['data']['q']}
                    unicorn_fied_data['data'].append(data)
            elif stream_data['data']['e'] == '24hrTicker':
                try:
                    if stream_data['stream']:
                        pass
                except KeyError:
                    stream_data['stream'] = '!ticker@arr'
                unicorn_fied_data = {'stream_type': stream_data['stream'],
                                     'event_type': stream_data['data']['e'],
                                     'data': []}
                try:
                    for item in stream_data['items']:
                        data = {'stream_type': stream_data['stream'],
                                'event_type': item['e'],
                                'event_time': item['E'],
                                'symbol': item['s'],
                                'price_change': item['p'],
                                'price_change_percent': item['P'],
                                'weighted_average_price': item['w'],
                                'trade_before_24h_window': item['x'],
                                'last_price': item['c'],
                                'last_quantity': item['Q'],
                                'best_bid_price': item['b'],
                                'best_bid_quantity': item['B'],
                                'best_ask_price': item['a'],
                                'best_ask_quantity': item['A'],
                                'open_price': item['o'],
                                'high_price': item['h'],
                                'low_price': item['l'],
                                'total_traded_base_asset_volume': item['v'],
                                'total_traded_quote_asset_volume': item['q'],
                                'statistics_open_time': item['O'],
                                'statistics_close_time': item['C'],
                                'first_trade_id': item['F'],
                                'last_trade_id': item['L'],
                                'total_nr_of_trades': item['n']}
                        unicorn_fied_data['data'].append(data)
                except KeyError:
                    # Todo: KeyError: 'x'
                    # 'trade_before_24h_window': stream_data['data']['x'],
                    # Todo: KeyError: 'b'
                    # 'best_bid_price': stream_data['data']['b'],
                    # Todo: KeyError: 'B'
                    # 'best_bid_quantity': stream_data['data']['B'],
                    # Todo KeyError: 'a'
                    # 'best_ask_price': stream_data['data']['a'],
                    # Todo KeyError: 'A'
                    # 'best_ask_quantity': stream_data['data']['A'],
                    data = {'stream_type': stream_data['stream'],
                            'event_type': stream_data['data']['e'],
                            'event_time': stream_data['data']['E'],
                            'symbol': stream_data['data']['s'],
                            'price_change': stream_data['data']['p'],
                            'price_change_percent': stream_data['data']['P'],
                            'weighted_average_price': stream_data['data']['w'],
                            'last_price': stream_data['data']['c'],
                            'last_quantity': stream_data['data']['Q'],
                            'open_price': stream_data['data']['o'],
                            'high_price': stream_data['data']['h'],
                            'low_price': stream_data['data']['l'],
                            'total_traded_base_asset_volume': stream_data['data']['v'],
                            'total_traded_quote_asset_volume': stream_data['data']['q'],
                            'statistics_open_time': stream_data['data']['O'],
                            'statistics_close_time': stream_data['data']['C'],
                            'first_trade_id': stream_data['data']['F'],
                            'last_trade_id': stream_data['data']['L'],
                            'total_nr_of_trades': stream_data['data']['n']}
                    unicorn_fied_data['data'].append(data)
            elif stream_data['data']['e'] == 'depth':
                # Todo: KeyError: 'lastUpdateId'
                # 'last_update_id': stream_data['data']['lastUpdateId'],
                # Todo: KeyError: 'bids'
                # 'bids': stream_data['data']['bids'],
                # , 'asks': stream_data['data']['asks']
                unicorn_fied_data = {'stream_type': stream_data['stream'],
                                     'event_type': stream_data['data']['e'],
                                     'symbol': stream_data['stream'][:stream_data['stream'].find('@')].upper()}
            elif stream_data['data']['e'] == 'depthUpdate':
                # Todo: KeyError: 'bids'
                # 'bids': stream_data['data']['b'],
                unicorn_fied_data = {'stream_type': stream_data['stream'],
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['s'],
                                     'first_update_id_in_event': stream_data['data']['U'],
                                     'final_update_id_in_event': stream_data['data']['u'],
                                     'asks': stream_data['data']['a']}
            elif stream_data['data']['e'] == 'outboundAccountInfo':
                unicorn_fied_data = {'stream_type': '!userData@arr',
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'maker_commission_rate': stream_data['data']['m'],
                                     'taker_commission_rate': stream_data['data']['t'],
                                     'buyer_commission_rate': stream_data['data']['b'],
                                     'seller_commission_rate': stream_data['data']['s'],
                                     'can_trade': stream_data['data']['T'],
                                     'can_withdraw': stream_data['data']['W'],
                                     'can_deposit': stream_data['data']['D'],
                                     'balances': []}
                for item in stream_data['data']['B']:
                    new_item = {'asset': item['a'],
                                'free': item['f'],
                                'locked': item['l']}
                    unicorn_fied_data['balances'] += [new_item]
            elif stream_data['data']['e'] == 'balanceUpdate':
                unicorn_fied_data = {'stream_type': '!userData@arr',
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'asset': stream_data['data']['a'],
                                     'balance_delta': stream_data['data']['d'],
                                     'clear_time': stream_data['data']['T']}
            elif stream_data['data']['e'] == 'executionReport':
                unicorn_fied_data = {'stream_type': '!userData@arr',
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['s'],
                                     'client_order_id': stream_data['data']['c'],
                                     'side': stream_data['data']['S'],
                                     'order_type': stream_data['data']['o'],
                                     'time_in_force': stream_data['data']['f'],
                                     'order_quantity': stream_data['data']['q'],
                                     'order_price': stream_data['data']['p'],
                                     'stop_price': stream_data['data']['P'],
                                     'iceberg_quantity': stream_data['data']['F'],
                                     'ignore_g': stream_data['data']['g'],
                                     'original_client_order_id': stream_data['data']['C'],
                                     'current_execution_type': stream_data['data']['x'],
                                     'current_order_status': stream_data['data']['X'],
                                     'order_reject_reason': stream_data['data']['r'],
                                     'order_id': stream_data['data']['i'],
                                     'last_executed_quantity': stream_data['data']['l'],
                                     'cumulative_filled_quantity': stream_data['data']['z'],
                                     'last_executed_price': stream_data['data']['L'],
                                     'commission_amount': stream_data['data']['n'],
                                     'commission_asset': stream_data['data']['N'],
                                     'transaction_time': stream_data['data']['T'],
                                     'trade_id': stream_data['data']['t'],
                                     'ignore_I': stream_data['data']['I'],
                                     'is_order_working': stream_data['data']['w'],
                                     'is_trade_maker_side': stream_data['data']['m'],
                                     'ignore_M': stream_data['data']['M'],
                                     'order_creation_time': stream_data['data']['O'],
                                     'cumulative_quote_asset_transacted_quantity': stream_data['data']['Z'],
                                     'last_quote_asset_transacted_quantity': stream_data['data']['Y']}
            elif stream_data['data']['e'] == 'ORDER_TRADE_UPDATE':
                '''
                    url: https://binance-docs.github.io/apidocs/futures/en/#event-order-update
                    ex:
                    {
                        "e":"ORDER_TRADE_UPDATE",     // Event Type
                        "E":1568879465651,            // Event Time
                        "T":1568879465650,            // Transaction Time
                        "o":{                             
                                "s":"BTCUSDT",              // Symbol
                                "c":"TEST",                 // Client Order Id
                                // special client order id:
                                // starts with "autoclose-": liquidation order
                                // "adl_autoclose": ADL auto close order
                                "S":"SELL",                 // Side
                                "o":"TRAILING_STOP_MARKET", // Order Type
                                "f":"GTC",                  // Time in Force
                                "q":"0.001",                // Original Quantity
                                "p":"0",                    // Original Price
                                "ap":"0",                   // Average Price
                                "sp":"7103.04",             // Stop Price. Please ignore with TRAILING_STOP_MARKET order
                                "x":"NEW",                  // Execution Type
                                "X":"NEW",                  // Order Status
                                "i":8886774,                // Order Id
                                "l":"0",                    // Order Last Filled Quantity
                                "z":"0",                    // Order Filled Accumulated Quantity
                                "L":"0",                    // Last Filled Price
                                "N":"USDT",             // Commission Asset, will not push if no commission
                                "n":"0",                // Commission, will not push if no commission
                                "T":1568879465651,          // Order Trade Time
                                "t":0,                      // Trade Id
                                "b":"0",                    // Bids Notional
                                "a":"9.91",                 // Ask Notional
                                "m":false,                  // Is this trade the maker side?
                                "R":false,                  // Is this reduce only
                                "wt":"CONTRACT_PRICE",      // Stop Price Working Type
                                "ot":"TRAILING_STOP_MARKET",    // Original Order Type
                                "ps":"LONG",                        // Position Side
                                "cp":false,                     // If Close-All, pushed with conditional order
                                "AP":"7476.89",             // Activation Price, only puhed with TRAILING_STOP_MARKET order
                                "cr":"5.0",                 // Callback Rate, only puhed with TRAILING_STOP_MARKET order
                                "rp":"0"                            // Realized Profit of the trade
                            }
                        }
                '''
                unicorn_fied_data = {'stream_type': 'ORDER_TRADE_UPDATE',
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['o']['s'],  # Symbol
                                     'client_order_id': stream_data['data']['o']['c'],  # Client Order Id
                                     'side': stream_data['data']['o']['S'],  # Side
                                     'order_type': stream_data['data']['o']['o'],  # Order Type
                                     'time_in_force': stream_data['data']['o']['f'],  # Time in Force
                                     'order_quantity': stream_data['data']['o']['q'],  # Original Quantity
                                     'order_price': stream_data['data']['o']['p'],  # Original Price
                                     'order_avg_price': stream_data['data']['o']['ap'],  # Average Price
                                     'order_stop_price': stream_data['data']['o']['sp'],  # Stop Price.
                                     'current_execution_type': stream_data['data']['o']['x'],  # Execution Type
                                     'current_order_status': stream_data['data']['o']['X'],  # Order Status
                                     'order_id': stream_data['data']['o']['i'],  # Order Id
                                     'last_executed_quantity': stream_data['data']['o']['l'],
                                     'cumulative_filled_quantity': stream_data['data']['o']['z'],
                                     'last_executed_price': stream_data['data']['o']['L'],  # Last Filled Price
                                     'transaction_time': stream_data['data']['o']['T'],  # Order Trade Time
                                     'trade_id': stream_data['data']['o']['t'],  # Trade Id
                                     'net_pay': stream_data['data']['o']['b'],  # Ask Notional
                                     'net_selling_order_value': stream_data['data']['o']['a'],  # Ask Notional
                                     'is_trade_maker_side': stream_data['data']['o']['m'],
                                     'reduce_only': stream_data['data']['o']['R'],  # Is this reduce only
                                     'trigger_price_type': stream_data['data']['o']['wt'],  # Stop Price Working Type
                                     'order_price_type': stream_data['data']['o']['ot'],  # Original Order Type
                                     'position_side': stream_data['data']['o']['ps'],
                                     # Todo:
                                     # 'cumulative_quote_asset_transacted_quantity': stream_data['data']['cp'],
                                     # 'cumulative_quote_asset_transacted_quantity': stream_data['data']['AP'],
                                     # 'cumulative_quote_asset_transacted_quantity': stream_data['data']['cr'],
                                     'order_realized_profit': stream_data['data']['o']['rp']}  # Realized Profit
            elif stream_data['data']['e'] == 'ACCOUNT_UPDATE':
                '''
                    url: https://binance-docs.github.io/apidocs/futures/en/#event-balance-and-position-update
                    ex:
                       {
                        "e": "ACCOUNT_UPDATE",                // Event Type
                        "E": 1564745798939,                   // Event Time
                        "T": 1564745798938 ,                  // Transaction
                        "a":                                  // Update Data
                            {
                            "m":"ORDER",                      // Event reason type
                            "B":[                             // Balances
                                {
                                "a":"USDT",                   // Asset
                                "wb":"122624.12345678",       // Wallet Balance
                                "cw":"100.12345678"           // Cross Wallet Balance
                                },
                                {
                                "a":"BNB",           
                                "wb":"1.00000000",
                                "cw":"0.00000000"         
                                }
                            ],
                            "P":[
                                {
                                "s":"BTCUSDT",            // Symbol
                                "pa":"0",                 // Position Amount
                                "ep":"0.00000",            // Entry Price
                                "cr":"200",               // (Pre-fee) Accumulated Realized
                                "up":"0",                     // Unrealized PnL
                                "mt":"isolated",              // Margin Type
                                "iw":"0.00000000",            // Isolated Wallet (if isolated position)
                                "ps":"BOTH"                   // Position Side
                                }，
                                {
                                    "s":"BTCUSDT",
                                    "pa":"20",
                                    "ep":"6563.66500",
                                    "cr":"0",
                                    "up":"2850.21200",
                                    "mt":"isolated",
                                    "iw":"13200.70726908",
                                    "ps":"LONG"
                                },
                                {
                                    "s":"BTCUSDT",
                                    "pa":"-10",
                                    "ep":"6563.86000",
                                    "cr":"-45.04000000",
                                    "up":"-1423.15600",
                                    "mt":"isolated",
                                    "iw":"6570.42511771",
                                    "ps":"SHORT"
                                }
                            ]
                            }
                        } 
                '''
                unicorn_fied_data = {
                    'stream_type': 'ACCOUNT_UPDATE',
                    'event_type': stream_data['data']['e'],
                    'event_time': stream_data['data']['E'],
                    'transaction': stream_data['data']['T'],
                    'event_reason': stream_data['data']['a']['m'],
                    'balances': [],
                    'positions': []
                }

                for balance in stream_data['data']['a']['B']:
                    unicorn_fied_data['balances'].append({
                        'asset': balance['a'],
                        'wallet_balance': balance['wb'],
                        'cross_wallet_balance': balance['cw']
                    })

                for position in stream_data['data']['a']['P']:
                    unicorn_fied_data['positions'].append({
                        'symbol': position['s'],
                        'position_amount': position['pa'],
                        'entry_price': position['ep'],
                        'accumulated_realized': position['cr'],
                        'upnl': position['up'],
                        'margin_type': position['mt'],
                        'isolated_wallet': position['iw'],
                        'position_side': position['ps']
                    })
            elif stream_data['data']['e'] == 'MARGIN_CALL':
                '''
                    url: https://binance-docs.github.io/apidocs/futures/en/#event-margin-call
                    ex: {
                            "e":"MARGIN_CALL",      // Event Type
                            "E":1587727187525,      // Event Time
                            "cw":"3.16812045",      // Cross Wallet Balance. Only pushed with crossed position margin call
                            "p":[                   // Position(s) of Margin Call
                            {
                                "s":"ETHUSDT",      // Symbol
                                "ps":"LONG",        // Position Side
                                "pa":"1.327",       // Position Amount
                                "mt":"CROSSED",     // Margin Type
                                "iw":"0",           // Isolated Wallet (if isolated position)
                                "mp":"187.17127",   // Mark Price
                                "up":"-1.166074",   // Unrealized PnL
                                "mm":"1m,n.614445"     // Maintenance Margin Required
                            }
                            ]
                        }  
                '''
                unicorn_fied_data = {'stream_type': 'MARGIN_CALL',
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['p']['s'],
                                     'side': stream_data['data']['p']['ps'],
                                     'amount': stream_data['data']['p']['pa'],
                                     'type': stream_data['data']['p']['mt'],
                                     'wallet': stream_data['data']['p']['iw'],
                                     'price': stream_data['data']['p']['mp'],
                                     'pnl': stream_data['data']['p']['up'],
                                     'margin': stream_data['data']['p']['mm']}
            elif stream_data['data']['e'] == 'ACCOUNT_CONFIG_UPDATE':
                '''
                url: https://binance-docs.github.io/apidocs/futures/en/#event-order-update
                ex:
                {
                    "e":"ACCOUNT_CONFIG_UPDATE",       // Event Type
                    "E":1611646737479,                 // Event Time
                    "T":1611646737476,                 // Transaction Time
                    "ac":{                              
                    "s":"BTCUSDT",                     // symbol
                    "l":25                             // leverage
                    }
                }  
                '''
                unicorn_fied_data = {'stream_type': 'ACCOUNT_CONFIG_UPDATE',
                                     'event_type': stream_data['data']['e'],
                                     'event_time': stream_data['data']['E'],
                                     'symbol': stream_data['data']['ac']['s'],
                                     'leverage': stream_data['data']['ac']['l']
                                     }
        except TypeError as error_msg:
            BOT.log.critical(f"UnicornFy->binance_futures_websocket({str(unicorn_fied_data)}) - "
                             f"error: {str(error_msg)}")

        BOT.log.debug("UnicornFy->binance_futures_websocket(" + str(unicorn_fied_data) + ")")
        return unicorn_fied_data


class BinanceWebSocketApiProcessStreams(object):
    @staticmethod
    def process_stream_data(received_stream_data_json, stream_buffer_name="False"):
        #
        #  START HERE!
        #
        # `received_stream_data_json` contains one record of raw data from the stream
        # print it and you see the data like its given from Binance, its hard to work with them, because keys of
        # parameters are changing from stream to stream and they are not self explaining.
        #
        # So if you want, you can use the class `UnicornFy`, it converts the json to a dict and prepares the values.
        # `depth5` for example doesnt include the symbol, but the unicornfied set includes them, because the class
        # extracts it from the channel name, makes it upper size and adds it to the returned values.. just print both
        # to see the difference.
        # Github: https://github.com/LUCIT-Systems-and-Development/unicorn-fy
        # PyPI: https://pypi.org/project/unicorn-fy/

        print(f'{received_stream_data_json = }')
        exchange = "binance.com"
        if exchange == "binance.com" or exchange == "binance.com-testnet":
            unicorn_fied_stream_data = UnicornFy.binance_com_websocket(received_stream_data_json)
        elif exchange == "binance.com-futures" or exchange == "binance.com-futures-testnet":
            unicorn_fied_stream_data = UnicornFy.binance_com_futures_websocket(received_stream_data_json)
        elif exchange == "binance.com-margin" or exchange == "binance.com-margin-testnet":
            unicorn_fied_stream_data = UnicornFy.binance_com_margin_websocket(received_stream_data_json)
        elif exchange == "binance.com-isolated_margin" or exchange == "binance.com-isolated_margin-testnet":
            unicorn_fied_stream_data = UnicornFy.binance_com_margin_websocket(received_stream_data_json)
        elif exchange == "binance.je":
            unicorn_fied_stream_data = UnicornFy.binance_je_websocket(received_stream_data_json)
        elif exchange == "binance.us":
            unicorn_fied_stream_data = UnicornFy.binance_us_websocket(received_stream_data_json)
        else:
            app.logger.error("Not a valid exchange: " + str(exchange))

        # Now you can call different methods for different `channels`, here called `event_types`.
        # Its up to you if you call the methods in the bottom of this file or to call other classes which do what
        # ever you want to be done.
        try:
            if unicorn_fied_stream_data['event_type'] == "aggTrade":
                BinanceWebSocketApiProcessStreams.aggtrade(unicorn_fied_stream_data)
            elif unicorn_fied_stream_data['event_type'] == "trade":
                BinanceWebSocketApiProcessStreams.trade(unicorn_fied_stream_data)
            elif unicorn_fied_stream_data['event_type'] == "kline":
                BinanceWebSocketApiProcessStreams.kline(unicorn_fied_stream_data)
            elif unicorn_fied_stream_data['event_type'] == "24hrMiniTicker":
                BinanceWebSocketApiProcessStreams.miniticker(unicorn_fied_stream_data)
            elif unicorn_fied_stream_data['event_type'] == "24hrTicker":
                BinanceWebSocketApiProcessStreams.ticker(unicorn_fied_stream_data)
            elif unicorn_fied_stream_data['event_type'] == "depth":
                BinanceWebSocketApiProcessStreams.miniticker(unicorn_fied_stream_data)
            else:
                BinanceWebSocketApiProcessStreams.anything_else(unicorn_fied_stream_data)
        except KeyError:
            BinanceWebSocketApiProcessStreams.anything_else(unicorn_fied_stream_data)
        except TypeError:
            pass

    @staticmethod
    def aggtrade(stream_data):
        # print `aggTrade` data
        print("aggtrade")
        print(stream_data)

    @staticmethod
    def trade(stream_data):
        # print `trade` data
        print("trade")
        print(stream_data)

    @staticmethod
    def kline(stream_data):
        # print `kline` data
        print("kline")
        print(stream_data)

    @staticmethod
    def miniticker(stream_data):
        # print `miniTicker` data
        print("miniticker")
        print(stream_data)

    @staticmethod
    def ticker(stream_data):
        # print `ticker` data
        print("ticker")
        print(stream_data)

    @staticmethod
    def depth(stream_data):
        # print `depth` data
        print("depth")
        print(stream_data)

    @staticmethod
    def outboundAccountInfo(stream_data):
        # print `outboundAccountInfo` data from userData stream
        print("outboundAccountInfo")
        print(stream_data)

    @staticmethod
    def executionReport(stream_data):
        # print `executionReport` data from userData stream
        print("executionReport")
        print(stream_data)

    @staticmethod
    def anything_else(stream_data):
        print("anything_else")
        print(stream_data)


if __name__ == "__main__":
    print("Dont run this script, its for imports only!")
