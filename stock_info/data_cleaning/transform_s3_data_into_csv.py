import boto3
import json
import pandas as pd
import logging
import datetime as dt
import pytz

logger = logging.getLogger()
logger.setLevel(logging.INFO)
client = boto3.client('s3')

def parse_data_to_df(stock_info):
    df_temp = pd.DataFrame(stock_info)
    # rename the columns
    df_stock = pd.DataFrame()
    df_stock['date'] = pd.to_datetime(df_temp['date'])
    df_stock['stock_symbol'] = df_temp['證券代號']
    df_stock['stock_name'] = df_temp['證券名稱']
    df_stock['trade_volume_shared'] = df_temp['成交股數']
    df_stock['transaction'] = df_temp['成交筆數']
    df_stock['trade_value'] = df_temp['成交金額']
    df_stock['opening_price'] = df_temp['開盤價']
    df_stock['highest_price'] = df_temp['最高價']
    df_stock['lowest_price'] = df_temp['最低價']
    df_stock['closing_price'] = df_temp['收盤價']
    df_stock['dir'] = df_temp['漲跌(+/-)']
    df_stock['change'] = df_temp['漲跌價差']
    df_stock['last_best_bid_price'] = df_temp['最後揭示買價']
    df_stock['last_best_bid_volume'] = df_temp['最後揭示買量']
    df_stock['last_best_ask_price'] = df_temp['最後揭示賣價']
    df_stock['last_best_ask_volume'] = df_temp['最後揭示賣量']
    df_stock['price_earning_ratio'] = df_temp['本益比']
    df_stock = df_stock[df_stock['last_best_bid_price'] !='--']
    df_stock = df_stock[df_stock['last_best_ask_price'] !='--']
    df_stock = df_stock[df_stock['opening_price'] !='--']
    # transform data type
    df_stock['trade_volume_shared'] = df_stock['trade_volume_shared'].astype(int)
    df_stock['transaction'] = df_stock['transaction'].astype(int)
    df_stock['trade_value'] = df_stock['trade_value'].astype(float)
    df_stock['opening_price'] = df_stock['opening_price'].astype(float)
    df_stock['highest_price'] = df_stock['highest_price'].astype(float)
    df_stock['lowest_price'] = df_stock['lowest_price'].astype(float)
    df_stock['closing_price'] = df_stock['closing_price'].astype(float)
    df_stock['change'] = df_stock['change'].astype(float)
    df_stock['last_best_bid_price'] = df_stock['last_best_bid_price'].astype(float)
    df_stock['last_beast_bid_volume'] = df_stock['last_best_bid_volume'].astype(int)
    df_stock['last_best_ask_price'] = df_stock['last_best_ask_price'].astype(float)
    df_stock['last_beast_ask_volume'] = df_stock['last_best_ask_volume'].astype(int)
    df_stock = df_stock.sort_values(by=['date'])

    return df_stock

def put_object_to_s3(date, json_file, file_status=''):
    logging.info(date)

    response = client.put_object(
        ACL='public-read',
        Body=json_file,
        Bucket='serverless-stocks',
        Key='stockinfos/cleaned_data/{}({})'.format(date, file_status)
    )

    print(response)

    return response

def get_bucket_keys_from_s3():
    object_response = client.list_objects(Bucket='serverless-stocks')

    logger.info(len(object_response['Contents']))

    files = []
    for obj in object_response['Contents']:
        # eliminate the folder
        if (len(obj['Key']) > 20):
            files.append({
                "Key": obj['Key'],
                "date": obj['Key'].split('/')[-1][:-9]
            })

    logger.info(files)

    return files

def transform_data_into_df():
    files = get_bucket_keys_from_s3()
    print(files[0])

    for date_info in files:
        res = client.get_object(Bucket='serverless-stocks', Key=date_info['Key'])
        date_info['data'] = json.loads(res['Body'].read().decode('utf-8'))
    
    logger.info(files[0])
    logger.info(files[-1])

    stock_info = []
    for file_info in files:
        for data in file_info['data']:
            data['date'] = file_info['date']
            data['成交筆數'] = data['成交筆數'].replace(',','')
            data['成交股數'] = data['成交股數'].replace(',','')
            data['成交金額'] = data['成交金額'].replace(',','')
            data['開盤價'] = data['開盤價'].replace(',','')
            data['最高價'] = data['最高價'].replace(',','')
            data['最低價'] = data['最低價'].replace(',','')
            data['收盤價'] = data['收盤價'].replace(',','')
            data['最後揭示買價'] = data['最後揭示買價'].replace(',','')
            if (data['最後揭示買量'] == None):
                pass
            else:
                data['最後揭示買量'] = data['最後揭示買量'].replace(',','')
            data['最後揭示賣價'] = data['最後揭示賣價'].replace(',','')
            if (data['最後揭示賣量'] == None):
                pass
            else:
                data['最後揭示賣量'] = data['最後揭示賣量'].replace(',','')
            data['本益比'] = str(data['本益比']).replace(',','')
            stock_info.append(data)

    date = dt.datetime.today()
    tw_tz = pytz.timezone('Asia/Taipei')
    tw_date = tw_tz.localize(date)
    date_of_str = tw_date.strftime('%Y-%m-%d')

    df_stock = parse_data_to_df(stock_info)
    try:
        json_file = df_stock.to_json(orient='records', force_ascii=False)
        result = put_object_to_s3(date_of_str, json_file, 'success')
        logger.info('succeed')
    except:
        logger.info('failed')