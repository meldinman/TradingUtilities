import pandas as pd
from datetime import date, datetime

from sms_utils import send_sms
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

def run_alert_log_blocking():
    ALERTED = set()
    sched = BlockingScheduler()
    sched.add_job(send_alert_text, 'cron', day_of_week='mon-fri', hour='7-16', second='*/10',args=[ALERTED] )
    sched.start()
    
def run_alert_log_background():
    ALERTED = set()
    sched = BackgroundScheduler()
    sched.add_job(send_alert_text, 'cron', day_of_week='mon-fri', hour='7-16', second='*/10',args=[ALERTED] )
    sched.start()
    
def send_alert_text(alerted):
    alert_log = get_todays_file()
    alerts = unique_alert(alerted, alert_log)
    for alert in alerts:
        send_sms(alert)
        print(alert)
    if len(alerts) < 1:
        print("no new alerts found {}".format(datetime.now()))    
        
def get_todays_file():
    today = date.today()
    file_path = "alertlogging.Running Up.{}.csv".format(today.strftime("%Y%m%d"))
    try:
        alert_log = pd.read_csv(file_path)
    except FileNotFoundError:
        alert_log = []
        print("No file yet")
    return alert_log


        
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
        
def reset_alerted_daily(alerted):
    now = datetime.now()
    if ( now.hour == 7 and now.minute == 1 and now.second == 1 ) :
        alerted = set()
    return alerted
    
if __name__ == '__main__':
    run_alert_log_blocking()