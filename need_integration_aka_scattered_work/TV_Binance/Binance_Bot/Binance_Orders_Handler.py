#
import ccxt
import pandas as pd


class Binance_Orderbook_Handler:
    """Expects from BOT:
    self.log = flask_app.logging
    self.exchange = ccxt.{exchange_class}() e.g. ccxt.binance()
    """

    def get_orderbook(BOT, symbol: str, max_orderbook_depth: int = 5):
        order_book = BOT.exchange.fetch_order_book(symbol=symbol,
                                                   limit=max_orderbook_depth if max_orderbook_depth >= 5 else 5)

        # Pretty print orderbook asks and bids
        BOT.log.info(f'\n{"Timestamp"}       -    {"Datetime"}')
        BOT.log.info(f'{order_book["timestamp"]}   -   {order_book["datetime"]}')
        for order_book_side in ['asks', 'bids']:
            BOT.log.info(f"{order_book_side.capitalize()}:")
            for order_book_price, order_book_quantity in order_book[order_book_side]:
                BOT.log.info(f" {order_book_price}  -  {order_book_quantity}")

        return order_book

    @staticmethod
    def create_order_history_table(order_history):
        order_history_table = []
        for order in order_history:
            order_history_table.append({
                "id": order["id"],
                "symbol": order["symbol"],
                "side": order["side"],
                "type": order["type"],
                "price": order["price"],
                "amount": order["amount"],
                "filled": order["filled"],
                "remaining": order["remaining"],
                "status": order["status"],
                "timestamp": order["timestamp"],
                "datetime": order["datetime"],
                "fee": order["fee"],
            })
        return order_history_table

    def prepare_limit_price(BOT, order_book, quantity, side, last_price, max_orderbook_price_offset,
                            min_orderbook_price_offset):
        limit_price = None
        for bid_ask_price, bid_ask_volume in order_book['asks' if side == 'buy' else 'bids']:
            if bid_ask_volume >= quantity:
                BOT.log.info(f"bid_ask_price: {bid_ask_price}, bid_ask_volume: {bid_ask_volume}")

                # Check if the price is within the range we want to place our order
                # get the price offset from the last price
                price_offset = abs(bid_ask_price - last_price) / last_price
                BOT.log.info(f"{price_offset}% diff between last price and and limit price")
                if (price_offset >= min_orderbook_price_offset or min_orderbook_price_offset == -1) and (
                        price_offset <= max_orderbook_price_offset or max_orderbook_price_offset == -1):
                    limit_price = bid_ask_price
                    break
                else:
                    raise Exception(
                        f"Computed Limit Price {bid_ask_price} is not within the range of {min_orderbook_price_offset}"
                        f" and {max_orderbook_price_offset}"
                        f" if you want to remove this check, set min_orderbook_price_offset=-1 and"
                        f" max_orderbook_price_offset=-1 to \"None\"")

        if limit_price is None:
            raise Exception("Could not find a price in the orderbook that has enough volume to cover the quantity")

        return limit_price


class Binance_Orders_Handler(Binance_Orderbook_Handler):

    def open_position(BOT, last_price, side, quantity, symbol,
                      order_type='MARKET',
                      position_params=None,
                      max_orderbook_depth=5,
                      min_orderbook_price_offset=None,
                      max_orderbook_price_offset=None,
                      limit_forced_offset=None,
                      take_profit=None, stop_loss=None,
                      # Trailing Stop Loss
                      # BUY: the lowest price after order placed <= activationPrice, and the latest price >= the lowest price * (1 + callbackRate)
                      # SELL: the highest price after order placed >= activationPrice, and the latest price <= the highest price * (1 - callbackRate)
                      callbackRate=None,
                      activation_percentage=None,
                      place_orders_in_batch=False,
                      # For TRAILING_STOP_MARKET, if you got such error code.
                      # {"code": -2021, "msg": "Order would immediately trigger."}
                      # means that the parameters you send do not meet the following requirements:
                      #
                      # BUY: activationPrice should be smaller than the latest price.
                      # SELL: activationPrice should be larger than the latest price.
                      DCA_bool=None,
                      DCA_total_amount=None,
                      DCA_opposite_boundry_percentage=None,
                      DCA_number_of_steps=None,
                      ):

        if position_params is None:
            position_params = {'reduceOnly': False}

        takeProfitOrder = None
        stopLossOrder = None
        trailingStopLossOrder = None

        returning_order_dict = dict(
        )



        try:
            '''Position Opening'''
            BOT.log.info(f"Sending {order_type} order  - {side} {quantity} {symbol}")
            if order_type.lower() == 'market':
                position_order = BOT.exchange.create_order(symbol=symbol, side=side, price=None, type=order_type,
                                                           amount=quantity, params=position_params)
            elif order_type.lower() == 'limit':
                if not limit_forced_offset:
                    BOT.log.info(f'Using orderbook to calculate limit order price')
                    # Get orderbook to get the best bid/ask price
                    order_book = BOT.get_orderbook(symbol=symbol,
                                                   max_orderbook_depth=max_orderbook_depth)
                    #
                    # User quantity to calculate how deep in the orderbook we want to place our limit order
                    limit_price = BOT.prepare_limit_price(order_book, quantity, side, last_price,
                                                          max_orderbook_price_offset, min_orderbook_price_offset)
                else:
                    BOT.log.info(f'Using forced offset to calculate limit order price')
                    # Use forced offset to calculate what price we want to place our order
                    limit_price = last_price * (1 + limit_forced_offset) if side == 'buy' else last_price * (
                            1 - limit_forced_offset)
                # todo left here , when using the dca the gte behaviour is not working
                position_order = BOT.exchange.create_order(symbol=symbol, side=side, price=limit_price, type=order_type,
                                                           amount=quantity, params=position_params)
                returning_order_dict['position'] = position_order
            else:
                raise Exception(f"Order type {order_type} not supported")

            '''Trade Management - Take Profit and Stop Loss'''
            # Try to place take_profit and stop_loss orders, however if we fail to do so, we will cancel the order
            try:
                take_profit = float(take_profit)
                stop_loss = float(stop_loss)
            except:
                take_profit = None
                stop_loss = None

            if take_profit is not None and stop_loss is not None:
                try:
                    stopLossOrder, takeProfitOrder = BOT.add_tp_sl_to_order(order_json=position_order,
                                                                            take_profit=take_profit,
                                                                            stop_loss=stop_loss, stopLossParams=None,
                                                                            takeProfitParams=None)

                    BOT.log.info(f"stopLossOrder: {stopLossOrder}")
                    BOT.log.info(f"takeProfitOrder: {takeProfitOrder}")

                except Exception as e:
                    BOT.log.info(f"Error placing take_profit and stop_loss orders {e}")
                    try:
                        open_orders = BOT.exchange.fetch_open_orders(symbol=symbol)
                        open_order_ids = [order["id"] for order in open_orders]
                        if position_order['id'] in open_order_ids:
                            BOT.log.info(f"Canceling order {position_order['id']}")
                            BOT.exchange.cancel_order(position_order['id'], symbol=symbol)
                        else:
                            BOT.market_close_position(position_order)
                            # todo use limits as well here to limit blow

                    except Exception as e:
                        BOT.log.error(f"Error cancelling order {e}")

            '''Trade Management - Trailing Stop Loss'''
            # Try to place trailing stop loss orders, however if we fail to do so, we will cancel the order
            try:
                callbackRate = float(callbackRate)
                activation_percentage = float(activation_percentage)
            except:
                callbackRate = None
                activation_percentage = None

            if callbackRate is not None and activation_percentage is not None:

                callbackRate = round(callbackRate * 100,
                                     1)
                assert callbackRate >= 0.1 and callbackRate <= 5, "callbackRate should be 0.001 <= & <= 0.05"

                assert activation_percentage >= 0 and activation_percentage <= 1, "activation_percentage should be 0 <= & <= 1"
                activationPrice = float(position_order['price']) * (
                        1 + activation_percentage) if side == 'buy' else float(
                    position_order['price']) * (1 - activation_percentage)

                # binance only allows increments of 0.1% for trailing stop loss callbackRate
                # so we need to round it to the nearest 0.1%

                try:
                    trailingStopLossOrder = BOT.add_trailing_stop_loss_to_order(order_json=position_order,
                                                                                callbackRate=callbackRate,
                                                                                activationPrice=activationPrice)
                except Exception as e:
                    BOT.log.error(f"Error placing trailing stop loss order {e}")
                    try:
                        BOT.exchange.cancel_order(position_order['id'], symbol=symbol)
                    except Exception as e:
                        BOT.log.error(f"Error cancelling order {e}")
                        BOT.market_close_position(position_order)

        except Exception as e:
            BOT.log.error(f"an exception occured - {e}")
            return False

        if takeProfitOrder is not None:
            returning_order_dict['takeProfitOrder'] = takeProfitOrder
        if stopLossOrder is not None:
            returning_order_dict['stopLossOrder'] = stopLossOrder
        if trailingStopLossOrder is not None:
            returning_order_dict['trailingStopOrder'] = trailingStopLossOrder
        if DCA_bool:
            try:
                # DCA_step_length = position_order['price'] * DCA_opposite_boundry_percentage
                DCA_step_length = last_price * DCA_opposite_boundry_percentage
                DCA_quantity = DCA_total_amount / DCA_number_of_steps  # fixme the quantity must meet the min quantity of the symbol allowed

                for i in range(DCA_number_of_steps):
                    # DCA_price = position_order['price'] - DCA_step_length * (
                    #         i + 1) if side == 'buy' else position_order['price'] + DCA_step_length * (i + 1)
                    DCA_price = last_price - DCA_step_length * (
                            i + 1) if side == 'buy' else last_price + DCA_step_length * (i + 1)

                    BOT.log.info(f"Sending {order_type} order - {side} {DCA_quantity} {symbol}")
                    DCA_order = BOT.exchange.create_order(symbol=symbol, side=side, price=DCA_price,
                                                          type=order_type,
                                                          amount=DCA_quantity, params=position_params)
                    BOT.log.info(f"Limit order for {DCA_quantity} placed at {DCA_price} {symbol}")
                    returning_order_dict[f'DCA_order_{i}'] = DCA_order
            except Exception as e:
                BOT.log.error(f"an exception occured - {e}")

        return returning_order_dict

    def cancel_all_symbol_open_orders(BOT, symbol: str):
        # get ids of all open orders
        open_orders = BOT.exchange.fetch_open_orders(symbol=symbol)
        open_order_ids = [order["id"] for order in open_orders]
        # cancel all open orders

        # Set
        open_order_ids = list(set(open_order_ids))
        for order_id in open_order_ids:
            try:
                BOT.exchange.cancel_order(order_id, symbol=symbol)  # cancel order
            except Exception as e:
                BOT.log.error(f"Error cancelling order {e}")

        return {
            "orders_cancelled_ids": open_order_ids,
        }

    def add_tp_sl_to_order(BOT, order_json, take_profit, stop_loss, stopLossParams=None, takeProfitParams=None):
        # Set a stop loss and take profit orders to protect our position and to abide by our risk management rules.
        side = 'sell' if order_json['side'] == 'buy' else 'buy'
        order_price = order_json['price']
        stopLossPrice = order_price * (1 - stop_loss) if side == 'sell' else order_price * (1 + stop_loss)
        takeProfitPrice = order_price * (1 + take_profit) if side == 'sell' else order_price * (1 - take_profit)
        BOT.log.info(
            f"\tplacing stop loss {stopLossPrice} and take profit {takeProfitPrice} for order {order_json['id']}")
        #
        stopLossParams = {'stopPrice': stopLossPrice,
                          # 'closePosition': True,
                          # 'workingType': 'CONTRACT_PRICE',
                          'workingType': 'MARK_PRICE',
                          'reduceOnly': True,
                          'priceProtect': True,
                          'timeInForce': 'GTE_GTC',
                          # 'stop': 'loss'
                          } if stopLossParams is None else stopLossParams
        takeProfitParams = {
            'stopPrice': takeProfitPrice,  # THis is the price we want to sell at to make a profit
            # 'activationPrice': takeProfitPrice,  # this is the price we want to sell at to make a profit
            # 'closePosition': True,
            'workingType': 'MARK_PRICE',  # we want to sell at the price of the contract
            'reduceOnly': True,  # we want to only reduce our position and not open a new one
            'priceProtect': True,
            # this will ensure that we don't get liquidated if the price moves against us while we are waiting for the take profit order to be filled
            'timeInForce': 'GTE_GTC',

        } if takeProfitParams is None else takeProfitParams
        #
        # if order_json['type'] == 'limit':
        #     stopLossOrder = {}
        #     takeProfitOrder = {}
        #     # stopLossOrder = BOT.exchange.create_limit_sell_order(symbol=order_json['info']['symbol'],
        #     #                                                      amount=order_json['amount'],
        #     #                                                      price=stopLossPrice, params=stopLossParams)
        #     # takeProfitOrder = BOT.exchange.create_limit_sell_order(symbol=order_json['info']['symbol'],
        #     #                                                      amount=order_json['amount'],
        #     #                                                      price=takeProfitPrice, params=takeProfitParams)
        #
        #     stopLossOrder = BOT.exchange.createOrder(symbol=order_json['info']['symbol'], type='LIMIT', side=side,
        #                                              price=stopLossPrice, amount=order_json['amount'],
        #                                              params=stopLossParams)
        #     takeProfitOrder = BOT.exchange.createOrder(symbol=order_json['info']['symbol'], type='TAKE_PROFIT', side=side,
        #                                                price=takeProfitPrice,
        #                                                amount=order_json['amount'],
        #                                                params=takeProfitParams)
        # else:
        stopLossOrder = BOT.exchange.create_order(symbol=order_json['info']['symbol'], type='STOP', side=side,
                                                  price=stopLossPrice,
                                                  amount=order_json['amount'], params=stopLossParams)
        takeProfitOrder = BOT.exchange.create_order(symbol=order_json['info']['symbol'], type='TAKE_PROFIT',
                                                    side=side,
                                                    price=takeProfitPrice,
                                                    amount=order_json['amount'], params=takeProfitParams)

        return stopLossOrder, takeProfitOrder

    def add_trailing_stop_loss_to_order(BOT, order_json=None, callbackRate=None, activationPrice=None):
        BOT.log.info(
            f"placing trailing stop loss for order {order_json['id']} with callbackRate {callbackRate} and activationPrice {activationPrice}")
        # Set a stop loss and take profit orders to protect our position and to obide by our risk management rules.
        side = 'sell' if order_json['side'] == 'buy' else 'buy'
        # order_price = order_json['price']
        trailing_stop_params = {'callbackRate': callbackRate,
                                'workingType': 'MARKET_PRICE',
                                'reduceOnly': True,
                                'priceProtect': True,
                                'timeInForce': 'GTE_GTC',
                                'activationPrice': round(activationPrice, 2),
                                }
        BOT.log.info(f"trailing_stop_params: {trailing_stop_params}")
        trailingStopOrder = BOT.exchange.create_order(symbol=order_json['info']['symbol'], type='TRAILING_STOP_MARKET',
                                                      side=side,
                                                      amount=order_json['amount'], params=trailing_stop_params)

        return trailingStopOrder

    def market_close_position(BOT, order_json):

        print(f'{order_json = }')
        opposite_side = 'sell' if order_json['side'] == 'buy' else 'buy'

        print(f'side to exit position: {opposite_side}')
        try:
            # Cancel the open orders connected to the position
            BOT.cancel_all_symbol_open_orders(order_json['info']['symbol'])
            close_position = BOT.exchange.create_order(symbol=order_json['info']['symbol'], type="MARKET",
                                                       side=opposite_side,
                                                       amount=abs(order_json['amount']),
                                                       params={
                                                           "reduceOnly": True,
                                                           # "closePosition": True
                                                       }
                                                       )
            print(f'Closed position: {close_position}')

        except Exception as e:
            print('\n\nError in market_close_position() -', e)
            print(
                'Could not close position. Manual intervention required.')
            raise e
        return close_position
