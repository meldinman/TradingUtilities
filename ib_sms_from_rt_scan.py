import asyncio
from sms_utils import send_sms
import ib_insync as ibi
import pandas as pd
import datetime
ibi.util.startLoop()

POSITIONSIZE = 1000

class App:
    """
    read a csv with symbols and prices
    subscribe to IB market data
    Get ticks / high and check if above limit price (short strategies)
    print alert to console and send sms if new alert
    """
    async def run(self):
        self.ib = ibi.IB()
        alerted_list = []
        alert_df = self.get_alert_df()
        with await self.ib.connectAsync('127.0.0.1', 7497, clientId=1):
            contracts = self.get_contracts(alert_df)
            async for tickers in self.ib.pendingTickersEvent:
                for ticker in tickers:
                    ticker_limit = list(alert_df.LimitPrice[alert_df['Symbol'].str.match(ticker.contract.symbol)])[-1]
                    if max(ticker.ask, ticker.high) >= ticker_limit :
                        alerted_ticker = ticker.contract.symbol
                        if alerted_ticker not in alerted_list:
                            alert_string = self.print_alerts(alerted_ticker, ticker, ticker_limit)
                            alerted_list.append(alerted_ticker)
                            send_sms(str(alert_string))
                    self.ib.waitOnUpdate()
    
    def get_alert_df(self):
        """
        read csv and return dataframe
        """
        alert_df = pd.read_csv("sample_scan.txt", usecols=["Signal","Symbol","LimitPrice"])
        return alert_df
    
    def get_contracts(self, alert_df):
        """
        get symbols from dataframe
        create IB contract object
        subscribe to contract
        """
        contracts = [
            ibi.Stock(symbol, 'SMART', 'USD')
                    for symbol in list(alert_df.Symbol)]
        for contract in contracts:
            data = self.ib.reqMktData(contract)
            #self.ib.sleep()
        return contracts

    def print_alerts(self, alerted_ticker, ticker, limit_price):
        """
        get alerted ticker details
        print strings to console and pass object for sms function
        """
        alert_string = "{} - High:{} Limit:{} Size: {}".format(alerted_ticker,ticker.high,limit_price, round(POSITIONSIZE/limit_price))
        print("Symbol {} alert at {}".format(alerted_ticker, datetime.datetime.now())) 
        print(alert_string)
        return alert_string
    
    def stop(self):
        self.ib.disconnect()

if __name__ == "__main__":

    app = App()
    try:
        asyncio.run(app.run())
    except (KeyboardInterrupt, SystemExit):
        app.stop()


