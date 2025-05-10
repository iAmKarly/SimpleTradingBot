import sys
import MetaTrader5 as mt5

from Algo.SimpleAlgo1 import SimpleAlgo1
from Tools.MT5Trader import MT5Trader

def main():   
    symbol = 'XAUUSD'
    startPos = 0.01
    multiplyPos = 1.25
    profitMargin = 25
    interval = 300
    timeframe = mt5.TIMEFRAME_M5
    thresholdPos = 25

    trader = MT5Trader()
    trader.initialize()
    trader.login_account()
    
    simpleAlgo1 = SimpleAlgo1(trader, symbol, startPos, multiplyPos, profitMargin, interval, timeframe, thresholdPos)
    simpleAlgo1.runAlgo()

if __name__ == "__main__":
    main()
