import sys
sys.path.append('../get_stock_info')
from handler import put_object_to_s3, parse_stock_info
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
# s3
import boto3

# agent instance
ua = UserAgent()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def put_object_to_s3(date, json_file, file_status=''):
    print(date)
    client = boto3.client('s3')
    date_format = '{}-{}-{}'.format(date.year, date.month, date.day)

    response = client.put_object(
        ACL='public-read',
        Body=json_file,
        Bucket='serverless-stocks',
        Key='stockinfos/{}({})'.format(date_format, file_status)
    )

    print(response)

    return response

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
    # proxies = {
    #     'http': 'socks5h://localhost:9050',
    #     'https': 'socks5h://localhost:9050'
    # }
    request_count = 0
    while(date < today):
        print(date)
        logger.info(date)
        renew_tor_ip()
        # fake agent
        # randomAgent = ua.random
        # header = {
        #         "User-Agent": randomAgent,
        #         "X-Requested-With": "XMLHttpRequest"
        # }
        date_of_str = date.strftime('%Y%m%d')
        stock_url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={}&type=ALL'.format(date_of_str)
        print(stock_url)
        print(get_current_ip())
        logger.info(stock_url)

        # response = requests.post(stock_url, headers=header, proxies=proxies)
        response = requests.post(stock_url)
        try:
            df = parse_stock_info(response)
            json_file = df.to_json(orient='records', force_ascii=False)
            result = put_object_to_s3(date, json_file, 'success')
            print('succeed')
        except:
            print('passed')
            pass
        
        date = date + dt.timedelta(days=1)
