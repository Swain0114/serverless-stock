# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json
import pandas as pd
from dash.dependencies import Input, Output
# Cache
from flask_caching import Cache

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 60


@cache.memoize(timeout=TIMEOUT)
def query_data():
    df = pd.read_csv('../../data/cleaned-data(20200223).csv')
    df['trade_volume_shared'] = ['{:,}'.format(
        i) for i in df['trade_volume_shared']]

    df['transaction'] = ['{:,}'.format(
        i) for i in df['transaction']]

    df['trade_value'] = ['{:,}'.format(
        i) for i in df['trade_value']]

    df['opening_price'] = ['{:,}'.format(
        i) for i in df['opening_price']]

    df['closing_price'] = ['{:,}'.format(
        i) for i in df['closing_price']]

    df['change'] = ['{:,}'.format(
        i) for i in df['change']]

    df['price_earning_ratio'] = ['{:,}'.format(
        i) for i in df['price_earning_ratio']]

    return df


def get_name_drop_down(df):

    options = []

    for stock_name in df['stock_name']:
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


df = query_data()

print(df.columns)

app.layout = html.Div(children=[
    html.H1(children='Stock Dashboard'),
    html.Div(children='''
        股票名稱
    '''),
    dcc.Input(id='stock-name-text', value='台積電', type='text'),
    # TODO: 下拉選單效能太差，再想辦法解決
    # dcc.Dropdown(
    #     id='stock-name-drop-down',
    #     options=get_name_drop_down(df),
    #     value='台泥',
    #     searchable=False
    # ),
    dcc.Graph(
        id='stock-price',
        figure={
            'data': [
                # dict(
                #     x=df[df['stock_name'] == i]['date'],
                #     y=df[df['stock_name'] == i]['closing_price'],
                #     name=i
                # ) for i in df['stock_name'].unique()[0]
            ],
            'layout': {
                'title': '收盤價'
            }
        }
    ),
    html.Div(children='''
        起始日期
    '''),
    dcc.Dropdown(
        id='stock-date-drop-down',
        options=get_date_drop_down(df),
        value='2018-01-02',
        style={
            'height': '35px',
            'width': '150px'
        },
        searchable=False
    ),
    dash_table.DataTable(
        id='stock-table',
        columns=[
            {'name': i, 'id': i} for i in table_columns()
        ],
        # data = df.to_dict('records'),
        # data = '',
        page_size=50
    )
])


@app.callback(
    Output('stock-price', 'figure'),
    [Input('stock-name-text', 'value')]
    # [Input('stock-name-drop-down', 'value')]
)
def update_stock_price(stock_name):
    dff = df[df['stock_name'] == stock_name]

    return {
        'data': [
            dict(
                x=dff[dff['stock_name'] == stock_name]['date'],
                y=dff[dff['stock_name'] == stock_name]['closing_price'],
                name=stock_name
            )
        ],
        'layout': {
            'title': '{} 收盤價'.format(stock_name)
        }
    }


@app.callback(
    Output('stock-table', 'data'),
    [Input('stock-name-text', 'value'),
     Input('stock-date-drop-down', 'value')]
    # [Input('stock-name-drop-down', 'value'),
    #  Input('stock-date-drop-down', 'value')]
)
def update_stock_table(stock_name, stock_date):
    dff = df[df['stock_name'] == stock_name]
    dff = dff[dff['date'] >= stock_date]

    return dff.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
