# -*- coding: UTF-8 -*-
import logging
import json
import numpy as np
import pandas as pd
from io import StringIO
import requests
# 時間處理
import datetime as dt
import pytz
# s3
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_stock_info(response):
    f = StringIO(response.text)
    str_list = []

    for i in response.text.split('\n'):
        if (len(i.split('",')) == 17 and i[0] != '='):
            i = i.strip(",\r\n")
            str_list.append(i)

    return pd.read_csv(StringIO("\n".join(str_list)))


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


def get_stock(event, context):
    date = dt.datetime.today()
    logger.info(date)
    tw_tz = pytz.timezone('Asia/Taipei')
    tw_date = tw_tz.localize(date)

    date_of_str = tw_date.strftime('%Y%m%d')

    stock_url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_of_str + '&type=ALL'

    logger.info(stock_url)

    response = requests.post(stock_url)

    df = parse_stock_info(response)

    json_file = df.to_json(orient='records', force_ascii=False)

    result = put_object_to_s3(tw_date, json_file, 'success')

    response = {
        "statusCode": 200,
        "body": json.dumps(result)
    }

    return response





