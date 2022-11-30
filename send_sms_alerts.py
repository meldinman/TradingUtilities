import pandas as pd
from datetime import datetime
from sms_utils import send_sms

def unique_alert(alerted, alert_log):
    symbol_alerts = []
    if len(alert_log) > 0:
        firsts = alert_log.groupby('Symbol', as_index=False).first()
        alerted_reset = reset_alerted_daily(alerted)
        for symbol in firsts.Symbol:
            if symbol not in alerted_reset:
                alerted_reset.add(symbol)
                symbol_alert = firsts.loc[firsts.Symbol == symbol][['Symbol', 'TimeStamp', 'Price', 'Volume Today']]
                symbol_alerts.append(symbol_alert)
    return symbol_alerts

def send_alert_text(alerted, alert_log):
    alerts = unique_alert(alerted, alert_log)
    for alert in alerts:
        send_sms(alert)
        print(alert)
    if len(alerts) < 1:
        print("no new alerts found {}".format(datetime.now()))
        
def reset_alerted_daily(alerted):
    now = datetime.now()
    if ( now.hour == 7 and now.minute == 1 and now.second == 1 ) :
        alerted = set()
    return alerted