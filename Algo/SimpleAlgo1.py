import time
import MetaTrader5 as mt5

class SimpleAlgo1:
    def __init__(self, MT5trader, symbol, startPos, multiplyPos, profitMargin, interval, thresholdPos):
        self.MT5trader = MT5trader
        self.symbol = symbol
        self.startPos = startPos
        self.multiplyPos = multiplyPos
        self.profitMargin = profitMargin
        self.interval = interval
        self.timeframe = mt5.TIMEFRAME_M1
        self.thresholdPos = thresholdPos

    def openBuy(self):
        buyInfo = self.MT5trader.get_total_buy_info(self.symbol)
        buyLots = buyInfo['lots']
        minBuy = buyInfo['lowest']
        positions = buyInfo['positions']
        if not buyLots:
            self.MT5trader.open_buy_position(self.symbol, self.startPos)
        else:
            if self.MT5trader.get_price(self.symbol)['ask']  < minBuy - self.thresholdPos:
                nextLot = round(self.startPos * ((positions)**self.multiplyPos),2)
                self.MT5trader.open_buy_position(self.symbol, nextLot)

    def openSell(self):
        sellInfo = self.MT5trader.get_total_sell_info(self.symbol)
        sellLots = sellInfo['lots']
        maxSell = sellInfo['highest']
        positions = sellInfo['positions']
        if not sellLots:
            self.MT5trader.open_sell_position(self.symbol, self.startPos)
        else:
            if self.MT5trader.get_price(self.symbol)['bid']  > maxSell + self.thresholdPos:
                nextLot = round(self.startPos * ((positions)**self.multiplyPos),2)
                self.MT5trader.open_sell_position(self.symbol, nextLot)

    def closeBuy(self):
        break_even = self.MT5trader.get_buy_break_even_price(self.symbol)
        if (break_even and (self.MT5trader.get_price(self.symbol)['ask'] > (break_even + self.profitMargin))):
            profit = self.MT5trader.get_total_buy_info(self.symbol)['profits']
            self.MT5trader.close_buy_positions(self.symbol)
            print(f'Closed all buy position with profit of {profit}')
        
    def closeSell(self):
        break_even = self.MT5trader.get_sell_break_even_price(self.symbol)
        if (break_even and (self.MT5trader.get_price(self.symbol)['bid'] < (break_even - self.profitMargin))):
            profit = self.MT5trader.get_total_sell_info(self.symbol)['profits']
            self.MT5trader.close_sell_positions(self.symbol)
            print(f'Closed all sell position with profit of {profit}')

    def checkOpenPositions(self):
        self.openBuy()
        self.openSell() 

    def checkClosePositions(self):
        self.closeBuy()
        self.closeSell()

    def wait_for_new_candle(self):
        last_candle_time = None

        while True:
            candles = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 2)
            if candles is None or len(candles) < 2:
                print(f"Failed to get candles for {self.symbol}")
                time.sleep(5)
                continue

            current_time = candles[-1]['time']

            if last_candle_time is None:
                last_candle_time = current_time

            if current_time > last_candle_time:
                return current_time

            time.sleep(5)

    def runAlgo(self):
        till5 = 0
        while True:
            try:
                new_candle_time = self.wait_for_new_candle()
                self.checkOpenPositions()
                till5 += 1
                if till5 >= 5:
                    self.checkClosePositions()
                    till5 = 0

            except Exception as e:
                print("❌ Error in runAlgo:", e)
                time.sleep(60)
