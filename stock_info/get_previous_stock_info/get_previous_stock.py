import sys
sys.path.append('../get_stock_info')
from handler import put_object_to_s3
import requests
import datetime as dt
import pytz
import numpy as np
import pandas as pd
import logging
# Tor
import time
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent

# agent instance
ua = UserAgent()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_current_ip():
    session = requests.session()

    # TO Request URL with SOCKS over TOR
    session.proxies = {}
    session.proxies['http'] = 'socks5h://localhost:9050'
    session.proxies['https'] = 'socks5h://localhost:9050'
    proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }

    try:
        # r = session.get('http://httpbin.org/ip')
        r = requests.get('http://httpbin.org/ip', proxies=proxies)
    except Exception as e:
        print(str(e))
    else:
        return r.text

def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(
            password='Swain')
        controller.signal(Signal.NEWNYM)

def get_stock_before(date):
    today = dt.datetime.today()
    request_count = 0
    while(date < today):
        logger.info(date)
        tw_tz = pytz.timezone('Asia/Taipei')
        tw_date = tw_tz.localize(date)
        if (request_count % 5 == 0):
            print('Old IP address: {}'.format(get_current_ip()))
            renew_tor_ip()
            print('New IP address: ${}'.format(get_current_ip()))
            randomAgent = ua.random
            print('Agent {}'.format(randomAgent))
            header = {
                "User-Agent": randomAgent,
                "X-Requested-With": "XMLHttpRequest"
            }

        date_of_str = tw_date.strftime('%Y%m%d')
        stock_url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_of_str + '&type=ALL'
        logger.info(stock_url)

        response = requests.post(stock_url)

        try:
            df = parse_stock_info(response)
            json_file = df.to_json(orient='records', force_ascii=False)

            result = put_object_to_s3(tw_date, json_file, 'success')
        except:
            pass
        
        date = date + dt.timedelta(days=1)
