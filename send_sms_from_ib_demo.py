import asyncio
from trade_ideas.sms_utils import send_sms
import ib_insync as ibi
import pandas as pd
import datetime
import win32api

ibi.util.startLoop()

POSITION_SIZE = 1000


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
        with await self.ib.connectAsync("127.0.0.1", 7496, clientId=200):
            contracts = self.get_contracts(alert_df)
            async for tickers in self.ib.pendingTickersEvent:
                for ticker in tickers:
                    if type(ticker.contract.symbol) == str:
                        ticker_df = alert_df[
                            alert_df["Symbol"] == ticker.contract.symbol
                        ].iloc[-1]
                        short_trigger = max(ticker.last, ticker.high)
                        long_trigger = min(ticker.last, ticker.low)
                        if (
                            ticker_df.OrderSide == -1
                            and short_trigger >= ticker_df.LimitPrice
                        ) or (
                            ticker_df.OrderSide == 1
                            and long_trigger <= ticker_df.LimitPrice
                        ):
                            alerted_ticker = ticker.contract.symbol
                            if alerted_ticker not in alerted_list:
                                alert_string = self.print_alert_string(
                                    ticker_df,
                                    ticker,
                                )
                                alerted_list.append(alerted_ticker)
                        self.ib.waitOnUpdate()

    def get_alert_df(self):
        """
        read csv and return dataframe
        """
        alert_df = pd.read_csv("candidate_example.csv")
        return alert_df

    def get_contracts(self, alert_df):
        """
        get symbols from dataframe
        create IB contract object
        subscribe to contract
        """
        contracts = [
            ibi.Stock(symbol, "SMART", "USD") for symbol in set(alert_df.Symbol)
        ]
        for contract in contracts:
            data = self.ib.reqMktData(contract)
        return contracts

    def print_alert_string(self, ticker_df, ticker):
        """
        get alerted ticker details
        print strings to console and pass object for sms function
        """
        alert_string = "{} - {} - {} Lmt:{} S:{} Side: {}".format(
            ticker_df.StrategyName,
            ticker_df.Symbol,
            self.get_trigger_price(ticker_df.OrderSide, ticker),
            ticker_df.LimitPrice,
            round(POSITION_SIZE / ticker_df.LimitPrice),
            self.get_ticker_side(ticker_df.OrderSide),
        )
        print(
            "Symbol {} alerted at {} for {}".format(
                ticker_df.Symbol, datetime.datetime.now(), ticker_df.StrategyName
            )
        )
        print(alert_string)
        send_sms(str(alert_string))
        win32api.MessageBox(0, str(ticker_df.LimitPrice), str(ticker_df.Symbol), 0x00001000)
        return alert_string

    def get_ticker_side(self, ticker_side):
        """
        get string to print for side of ticker
        """
        if ticker_side == -1:
            order_side = "Short"
        else:
            order_side = "Long"
        return order_side

    def get_trigger_price(self, ticker_side, ticker):
        """
        get string to print if trigger is highs for short or lows for long
        """
        if ticker_side == -1:
            trigger_price = "H: {}".format(max(ticker.last, ticker.high))
        else:
            trigger_price = "L: {}".format(min(ticker.last, ticker.low))
        return trigger_price

    def stop(self):
        self.ib.disconnect()


if __name__ == "__main__":

    app = App()
    try:
        asyncio.run(app.run())
    except (KeyboardInterrupt, SystemExit):
        app.stop()
