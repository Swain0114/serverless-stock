import pandas as pd


def get_name_drop_down(df):
    options = []

    for stock_name in df['stock_name'].unique():
        dic = {
            'label': stock_name,
            'value': stock_name
        }
        options.append(dic)
    return options


def get_date_drop_down(df):
    options = []

    for stock_date in df['date'].unique():
        dic = {
            'label': stock_date,
            'value': stock_date
        }
        options.append(dic)
    return options


def table_columns():
    return ['date', 'stock_symbol', 'stock_name', 'trade_volume_shared', 'transaction', 'trade_value',
            'opening_price', 'closing_price', 'change', 'price_earning_ratio']


def get_columns_drop_down():
    columns = ['stock_symbol', 'stock_name', 'trade_volume_shared', 'transaction', 'trade_value',
               'opening_price', 'closing_price', 'change', 'price_earning_ratio']

    options = []
    for e in columns:
        dic = {
            'label': e,
            'value': e
        }
        options.append(dic)
    return options
