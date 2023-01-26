# TradingUtilities

This is a working collection of some simple tools I have developed to make my trading easier and ensure I dont miss trades.

Feel free to use these tools and make them better!

Things you will need to do:
  1) pip install ib_insync if using ib monitoring
  2) make sure you have your IB gateway or TWS connection running. I wont go into all that but there's plenty of info out there on this.
  3) edit the sms_utils file to add you number and email address and app password (NOT YOUR GMAIL PASSWORD) https://support.google.com/accounts/answer/185833?hl=en
  4) I'm sure there's more stuff, which I will add here

Files to use:
  1) try the python notebook to see how log files are being read and monitored. 
  2) I keep the monitor_and_sms.py file running to send sms alerts from TradeIdeas Logs
  3) send_sms_from_ib_monitor.py similarly reads csv files with a list of candidates and prices (in this case a sample_scan file from RealTest) and use IB tick data to         send an SMS when prices are hit 
