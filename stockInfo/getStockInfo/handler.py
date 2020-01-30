# -*- coding: UTF-8 -*-

import json
import numpy as np
import pandas as pd
from io import StringIO
import requests
import datetime
import boto3


def parse_stock_info(response):
    f = StringIO(response.text)
    strList = []

    for i in response.text.split('\n'):
        if (len(i.split('",')) == 17 and i[0] != '='):
            i = i.strip(",\r\n")
            strList.append(i)

    return pd.read_csv(StringIO("\n".join(strList)))


def put_object_to_s3(dateOfStr, jsonFile):
    client = boto3.client('s3')
    response = client.put_object(
        ACL='public-read',
        Body=jsonFile,
        Bucket='serverless-stocks',
        Key='stockinfos/{}'.format(dateOfStr)
    )
    return response


def get_stock(event, context):
    date = datetime.date.today()
    dateOfStr = '{}{}{}'.format(date.year, date.month, date.day)

    # dateOfStr = '20200102'
    response = requests.post(
        'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + dateOfStr + '&type=ALL')

    df = parse_stock_info(response)

    jsonFile = df.to_json(orient='records', force_ascii=False)

    result = put_object_to_s3(dateOfStr, jsonFile)

    response = {
        "statusCode": 200,
        "result": result
    }

    return response
