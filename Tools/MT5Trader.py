import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

class MT5Trader:
    def __init__(self, env_path='./config/.env'):
        load_dotenv(dotenv_path=env_path)
        self.login = int(os.getenv("MT5_NUMBER"))
        self.password = os.getenv("MT5_PASSWORD")
        self.server = os.getenv("MT5_SERVER")
        self.path = os.getenv("MT5_PATH")
        self.connected = False

    def initialize(self, path=None):
        if not path:
            path = self.path
        if not mt5.initialize(path=path):
            raise Exception(f"MT5 Initialization failed: {mt5.last_error()}")
        self.connected = True
        print("MT5 Initialized")

    def login_account(self):
        if not mt5.login(self.login, password=self.password, server=self.server):
            mt5.shutdown()
            raise Exception(f"MT5 Login failed: {mt5.last_error()}")
        print("MT5 Login successful")

    def open_buy_position(self, symbol, lot):
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise Exception(f"Failed to get tick data for {symbol}")
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 10,
            "magic": 123456,
            "comment": "Python Buy Order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise Exception(f"Order failed: {result}")
        print("Buy order placed:", result)

    def open_sell_position(self, symbol, lot):
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise Exception(f"Failed to get tick data for {symbol}")
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": tick.bid,
            "deviation": 10,
            "magic": 123456,
            "comment": "Python Buy Order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise Exception(f"Order failed: {result}")
        print("Sell order placed:", result)

    def close_buy_positions(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if not positions:
            print(f"No open positions for {symbol}")
            return

        buy_positions = [pos for pos in positions if pos.type == mt5.ORDER_TYPE_BUY]

        if not buy_positions:
            print(f"No BUY positions to close for {symbol}")
            return

        for pos in buy_positions:
            price = mt5.symbol_info_tick(symbol).bid  # You sell to close a buy
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": price,
                "deviation": 10,
                "magic": 123456,
                "comment": "Python close BUY",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"❌ Failed to close BUY position {pos.ticket}: {result}")
            else:
                print(f"✅ Closed BUY position {pos.ticket}")


    def close_sell_positions(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if not positions:
            print(f"No open positions for {symbol}")
            return

        sell_positions = [pos for pos in positions if pos.type == mt5.ORDER_TYPE_SELL]

        if not sell_positions:
            print(f"No SELL positions to close for {symbol}")
            return

        for pos in sell_positions:
            price = mt5.symbol_info_tick(symbol).ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "deviation": 10,
                "magic": 123456,
                "comment": "Python close SELL",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"❌ Failed to close SELL position {pos.ticket}: {result}")
            else:
                print(f"✅ Closed SELL position {pos.ticket}")

    def get_total_buy_info(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            return {"lots": None, "value": None, 'positions': None, "lowest": None}

        tick = mt5.symbol_info_tick(symbol)
        symbol_info = mt5.symbol_info(symbol)
        if not tick or not symbol_info:
            raise Exception("Failed to get symbol info or tick")

        contract_size = symbol_info.trade_contract_size
        total_lots = 0.0
        total_value = 0.0

        for pos in positions:
            if pos.type == mt5.ORDER_TYPE_BUY:
                total_lots += pos.volume
                total_value += pos.volume * contract_size * tick.ask
        if positions:
            lowest = min(positions, key=lambda p: p.price_open).price_open
        else:
            lowest = None
        positions = len(positions)

        return {"lots": total_lots, "value": total_value, 'positions': positions, "lowest": lowest}

    
    def get_total_sell_info(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            return {"lots": None, "value": None, 'positions': None, "lowest": None}

        tick = mt5.symbol_info_tick(symbol)
        symbol_info = mt5.symbol_info(symbol)
        if not tick or not symbol_info:
            raise Exception("Failed to get symbol info or tick")

        contract_size = symbol_info.trade_contract_size
        total_lots = 0.0
        total_value = 0.0

        for pos in positions:
            if pos.type == mt5.ORDER_TYPE_SELL:
                total_lots += pos.volume
                total_value += pos.volume * contract_size * tick.bid

        if positions:
            highest = max(positions, key=lambda p: p.price_open).price_open
        else:
            highest = None
        
        positions = len(positions)

        return {"lots": total_lots, "value": total_value, 'positions': positions, "highest": highest}
    
    def get_buy_break_even_price(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            raise Exception("Failed to retrieve positions")

        total_volume = 0.0
        total_cost = 0.0

        for pos in positions:
            if pos.type == mt5.ORDER_TYPE_BUY:
                total_volume += pos.volume
                total_cost += pos.volume * pos.price_open

        if total_volume == 0:
            return None

        break_even_price = total_cost / total_volume
        return break_even_price

    def get_sell_break_even_price(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            raise Exception("Failed to retrieve positions")

        total_volume = 0.0
        total_cost = 0.0

        for pos in positions:
            if pos.type == mt5.ORDER_TYPE_SELL:
                total_volume += pos.volume
                total_cost += pos.volume * pos.price_open

        if total_volume == 0:
            return None

        break_even_price = total_cost / total_volume
        return break_even_price
    
    def ensure_symbol_ready(self, symbol):
        info = mt5.symbol_info(symbol)
        if info is None:
            raise Exception(f"Symbol '{symbol}' not found")
        if not info.visible:
            if not mt5.symbol_select(symbol, True):
                raise Exception(f"Symbol '{symbol}' is not visible and could not be selected")

    def get_price(self, symbol):
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise Exception(f"Failed to retrieve tick data for {symbol}")
        return {"bid": tick.bid, "ask": tick.ask}
    
    def shutdown(self):
        mt5.shutdown()
        print("MT5 connection closed")
