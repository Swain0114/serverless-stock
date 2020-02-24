# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
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

TIMEOUT = 60000


@cache.memoize(timeout=TIMEOUT)
def query_data():
    df = pd.read_csv('../../data/cleaned-data(20200223).csv')
    return df

def get_drop_down():
    df = query_data()
    print(df.head())

    options = []

    print(df['stock_name'])

    for stock_name in df['stock_name']:
        dic = {
            'label': stock_name,
            'value': stock_name
        }
        options.append(dic)
    return options

df = query_data()

print(df.columns)

app.layout = html.Div(children=[
    html.H1(children='Stock Dashboard'),
    html.Div(children='''
        Security Name
    '''),
    # dcc.Input(id='stock-name-text', value='台積電', type = 'text'),
    dcc.Dropdown(
        id='stock-name-drop-down',
        options= get_drop_down(),
        value = '台積電',
        searchable = True
    ),
    dcc.Graph(
        id='stock-price',
        figure={
            'data': [
                dict(
                    x = df[df['stock_name'] == i]['date'],
                    y = df[df['stock_name'] == i]['closing_price'],
                    name = i
                ) for i in df['stock_name'].unique()[:10]
            ],
            'layout': {
                'title': 'Closing Price'
            }
        }
    )
])

@app.callback(
    Output('stock-price', 'figure'),
    [Input('stock-name-drop-down', 'value')]
)
def update_stock_drop_down(stock_name):
    dff = df[df['stock_name'] == stock_name]

    print(df)

    return {
        'data': [
            dict(
                x = dff[dff['stock_name'] == stock_name]['date'],
                y = dff[dff['stock_name'] == stock_name]['closing_price'],
                name = stock_name
            )
        ],
        'layout': {
            'title': '{} Closing Price'.format(stock_name)
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)