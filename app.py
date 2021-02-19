import datetime
from datetime import date,datetime, timedelta
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import requests
import json
import os
from helpers import get_dataframe, build_piechart, process_df

# Shopify API credentials
CA_key = os.getenv('CA_key')
CA_pass = os.environ.get('CA_pass')

US_key = os.getenv('US_key')
US_pass = os.environ.get('US_pass')

# Initiate Dash server
server = Flask(__name__)
app = dash.Dash(server=server)

global table_name
table_name = 'shopifydata1'

global bgcolor
bgcolor = '#000'

global txcolor
txcolor = '#ebebeb'

global utility_colors
utility_colors = ['Aluminum', 'Black']

global knit_colors
knit_colors = ['Space Black', 'Ash White', 'Black', 'Clay Blue', 'Light Grey', 'Wine', 'Moss', 'Charcoal']

global leather_colors
leather_colors = ['Light Grey', 'Black', 'Ceramic White', 'White/Gum', 'Titanium', 'Sand', 'Space Black', 'Navy Suede']

global discount_codes_of_interest
discount_codes_of_interest = ['exchange','braden','warranty','cascacreator','error','endlessflight']

global colors
colors = ['#F8BF14','#ebebeb', '#a99e8d','#ffffff','#2a2b2c','#94a9af','#4e75d4','#ffbb00']

app.layout = html.Div(
    [
        html.H1("Casca sales data analyzer", style={"textAlign": "center",'color':txcolor, 'margin-bottom':'10px','margin-top':'-5px','font-size':'60px'}),
        dcc.DatePickerRange(
                        id='date_range',
                        day_size = 50,
                        reopen_calendar_on_clear=True,
                        clearable = True,
                        min_date_allowed = date(2018, 6, 1),
                        max_date_allowed = date.today(),
                        # initial_visible_month = date(2020, 7, 1),
                        start_date = date(2021, 1, 1),
                        end_date = date(2021, 1, 31),
                        minimum_nights = 0,
                        updatemode = 'singledate',
                        className = 'dcc_compon',
                        style={'display':'flex', 'justifyContent':'center', 'margin-bottom':'15px','color':txcolor}),
        
        
        html.Div(id='intermediate-value', style={'display': 'none'}),
        
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='dropdown_1',
                        options=[
                            {'label': 'Total Orders', 'value': 'Total Orders'},
                            {'label': 'Orders with SmartFit', 'value': 'Orders with SmartFit'},
                            {'label': 'Shoe Models Sold', 'value': 'Shoe Models Sold'},
                            {'label': 'SmartFit Sold', 'value': 'SmartFit Sold'},
                            {'label': 'Other Products Sold', 'value': 'Other Products Sold'},
                            {'label': 'Avro Leather Colors', 'value': 'Avro Leather Colors'},
                            {'label': 'Avro Leather Genders', 'value': 'Avro Leather Genders'},
                            {'label': 'Avro Knit Colors', 'value': 'Avro Knit Colors'},
                            {'label': 'Avro Knit Genders', 'value': 'Avro Knit Genders'},
                            {'label': 'Avro Utility Colors', 'value': 'Avro Utility Colors'},
                            {'label': 'Avro Utility Genders', 'value': 'Avro Utility Genders'},
                            {'label': 'Discounts Issued', 'value': 'Discounts Issued'},
                            {'label': 'Pre-Orders', 'value': 'Pre-Orders'},
                            {'label': 'Purchase Country', 'value': 'Purchase Country'},
                            {'label': 'Purchase Location', 'value': 'Purchase Location'}
                        ],
                        value='Total Orders',
                        clearable = False
                        ),
                    ],style={'width':'40%','margin': '0 auto','margin-bottom':'5px'}),
                html.Div([
                    dcc.Checklist(
                    id='country_picker_1',
                    options=[
                        {'label': 'Canada', 'value': 'CA'},
                        {'label': 'USA', 'value': 'US'}
                    ],
                    value=['CA', 'US'],
                    style={'display':'flex', 'justifyContent':'center','color':txcolor}),
                    ]),

                html.Div([
                    dcc.Graph(
                        id = 'pie_chart_1',
                        config = {'displayModeBar': 'hover'},
                        ),
                    ],style={'width':'100%'}),

                ],style={'width':'50%',"border":"1px grey solid",'padding':'10px','margin':'10px','margin-right':'5px','border-radius':'5px'}
            ),

            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='dropdown_2',
                        options=[
                            {'label': 'Total Orders', 'value': 'Total Orders'},
                            {'label': 'Orders with SmartFit', 'value': 'Orders with SmartFit'},
                            {'label': 'Shoe Models Sold', 'value': 'Shoe Models Sold'},
                            {'label': 'SmartFit Sold', 'value': 'SmartFit Sold'},
                            {'label': 'Other Products Sold', 'value': 'Other Products Sold'},
                            {'label': 'Avro Leather Colors', 'value': 'Avro Leather Colors'},
                            {'label': 'Avro Leather Genders', 'value': 'Avro Leather Genders'},
                            {'label': 'Avro Knit Colors', 'value': 'Avro Knit Colors'},
                            {'label': 'Avro Knit Genders', 'value': 'Avro Knit Genders'},
                            {'label': 'Avro Utility Genders', 'value': 'Avro Utility Genders'},
                            {'label': 'Discounts Issued', 'value': 'Discounts Issued'},
                            {'label': 'Pre-Orders', 'value': 'Pre-Orders'},
                            {'label': 'Purchase Country', 'value': 'Purchase Country'},
                            {'label': 'Purchase Location', 'value': 'Purchase Location'}
                        ],
                        value='Orders with SmartFit',
                        clearable = False
                        ),
                    ],style={'width':'40%','margin': '0 auto','margin-bottom':'5px'}),
                html.Div([
                    dcc.Checklist(
                    id='country_picker_2',
                    options=[
                        {'label': 'Canada', 'value': 'CA'},
                        {'label': 'USA', 'value': 'US'}
                    ],
                    value=['CA', 'US'],
                    style={'display':'flex', 'justifyContent':'center','color':txcolor}),
                    ]),

                html.Div([
                    dcc.Graph(
                        id = 'pie_chart_2',
                        config = {'displayModeBar': 'hover'},
                        ),
                    ],style={'width':'100%'}),

                ],style={'width':'50%',"border":"1px grey solid",'padding':'10px','margin':'10px','margin-left':'5px','border-radius':'5px'}
            )
        ],style={'width':'100%','display':'flex','margin-top':'30px'}),

        

        html.Div([
            dcc.Checklist(
                id='country_picker',
                options=[
                    {'label': 'Canada', 'value': 'CA'},
                    {'label': 'USA', 'value': 'US'}
                ],
                value=['CA', 'US'],
                style={'display':'flex', 'justifyContent':'center','margin-top':'10px','color':txcolor}
                ),
            
            html.Div([
                dcc.Graph(
                    id = 'bar-chart',
                    config = {'displayModeBar': 'hover'},
                    ),],
                style={'width':'100%','display':'inline-block'}
                )
            ],style={"border":"1px grey solid",'padding':'0px','margin':'10px','margin-top':'0px','border-radius':'5px'})

    ],
    style={"background-color": bgcolor,'margin':'10px'},
)


@app.callback(
    Output('intermediate-value', 'children'),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"))
def update_df(start_date,end_date):
    df = get_dataframe(start_date,end_date,CA_key, CA_pass, US_key, US_pass)
    df_json = df.to_json(orient="split")
    df.to_csv('output.csv')
    return df_json

@app.callback(
    Output("bar-chart", "figure"),
    Input('country_picker','value'),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"),
    Input('intermediate-value', 'children'))
def update_prov_table(country_3,start_date,end_date,df_json):

    df = pd.read_json(df_json, orient='split')

    if 'CA' not in country_3:
        df = df[df['currency']!='CAD']
    if 'US' not in country_3:
        df = df[df['currency']!='USD']

    # remove time infomrmation from date
    df['created_at'] = pd.to_datetime(df['created_at']).apply(lambda x: x.date())
    
    # How many total_price orders?
    qty_all_orders = len(df)

    #remove exchanges
    df_temp=df[df["discount_code"].str.contains('exchange',na=False,case=False)==False]

    #convert total price to float
    df_temp['total_price'] = pd.to_numeric(df_temp['total_price'], downcast="float")

    # Whate states are customers in?
    states_dict = {}
    for index, row in df_temp.iterrows():
        if row['province_code'] != None:
            if row['province_code'] in states_dict:
                states_dict[row['province_code']]+=1
            else: states_dict[row['province_code']] = 1

    states_df = pd.DataFrame({'state':list(states_dict.keys()),'number of orders':list(states_dict.values())})
    states_df['Color']='#a99e8d'
    canada=['AB','BC','SK','MB','ON','QC','NL','NB','NS','PE','YK','NT','NU']
    for index, row in states_df.iterrows():
        if row['state'] in canada:
            states_df['Color'][index]= 'red'

    return { # in store?
        'data': [go.Bar(x= states_df['state'],#list(states_dict.keys()),
                        y = states_df['number of orders'],
                        textposition = 'auto',
                        marker={'color':states_df['Color']})
        ],

        'layout': go.Layout(
            titlefont = {
                'color': txcolor,
                'size': 15},
            margin=dict(t=50),
            title = {
                'text': 'Purchase Province/State<sup>*</sup><sup>*</sup>',

                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor),
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            #width = '100%',
            plot_bgcolor = '#ebebeb',
            paper_bgcolor = bgcolor
        ),

    }

@app.callback(
    Output('pie_chart_1', 'figure'),
    Input('country_picker_1','value'),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"),
    Input("dropdown_1", "value"),
    Input('intermediate-value', 'children'))
def update_graph(country_1,start_date,end_date,dropdown_value_1,df_json):

    df = pd.read_json(df_json, orient='split')

    if 'CA' in country_1:
        CA=True
    else: CA=False
    if 'US' in country_1:
        US=True
    else: US=False

    leather_color_dict,leather_size_dict,knit_color_dict,knit_size_dict,utility_color_dict,utility_size_dict,qty_all_orders,qty_giveaways,Smartfit_order_count,Country_CA,Country_US,PreOrder_yes,PreOrder_no,total_price_sales_usd,total_price_sales_cad,qty_sales_orders,No_Smartfit_order_count,qty_utility_sold,qty_knit_sold,qty_leather_sold,shoes_sold,qty_smartfit_sold,qty_kepler_sold,qty_pascal_sold,qty_giftcard_sold,discount_code_qty_dict,Retail_store,Online=process_df(df,utility_colors,knit_colors,leather_colors,discount_codes_of_interest,CA,US)
    

    pie_chart_dict = {
    'Total Orders':{
        'labels':['Sales', 'Exhanges', 'Give Aways'],
        'values':[qty_sales_orders, discount_code_qty_dict['exchange'], qty_giveaways],
        'text': 'Orders Placed: {}<br> Total Sales USD: {}<br> Total Sales CAD: {}'.format(qty_all_orders,total_price_sales_usd,total_price_sales_cad)
        },
    'Orders with SmartFit':{
        'labels':['Orders with SmartFit', 'Orders without SmartFit'],
        'values':[Smartfit_order_count,  No_Smartfit_order_count],
        'text': 'Sales orders with and without SmartFit<sup>*</sup><sup>*</sup>'
        },
    'Shoe Models Sold':{
        'labels':['Avro Knit', 'Avro Leather', 'Utility'],
        'values':[qty_knit_sold, qty_leather_sold, qty_utility_sold],
        'text': 'Shoes Sold: {}<sup>*</sup><sup>*</sup>'.format(shoes_sold)
        },
    'SmartFit Sold':{
        'labels':['SmartFit'],
        'values':[qty_smartfit_sold],
        'text':'SmartFit Sold<sup>*</sup><sup>*</sup>'
        },
    'Other Products Sold':{
        'labels':['Kepler', 'Pascal', 'Giftcard'],
        'values':[qty_kepler_sold, qty_pascal_sold, qty_giftcard_sold],
        'text': 'Socks and Giftcards Sold<sup>*</sup><sup>*</sup>'
        },
    'Avro Leather Colors':{
        'labels':list(leather_color_dict.keys()),
        'values':list(leather_color_dict.values()),
        'text': 'Avro Leather Colors<sup>*</sup><sup>*</sup>'
        },
    'Avro Leather Genders':{
        'labels':list(leather_size_dict.keys()),
        'values':list(leather_size_dict.values()),
        'text': 'Avro Leather Genders<sup>*</sup><sup>*</sup>'
        },
    'Avro Knit Colors':{
        'labels':list(knit_color_dict.keys()),
        'values':list(knit_color_dict.values()),
        'text': 'Avro Knit Colors<sup>*</sup><sup>*</sup>'
        },
    'Avro Knit Genders':{
        'labels':list(knit_size_dict.keys()),
        'values':list(knit_size_dict.values()),
        'text': 'Avro Knit Genders<sup>*</sup><sup>*</sup>'
        },
    'Avro Utility Colors':{
        'labels':list(utility_color_dict.keys()),
        'values':list(utility_color_dict.values()),
        'text': 'Avro Utility Colors<sup>*</sup><sup>*</sup>'
        },
    'Avro Utility Genders':{
        'labels':list(utility_size_dict.keys()),
        'values':list(utility_size_dict.values()),
        'text': 'Avro Utility Genders<sup>*</sup><sup>*</sup>'
        },
    'Discounts Issued':{
        'labels':list(discount_code_qty_dict.keys()),
        'values':list(discount_code_qty_dict.values()),
        'text': 'Discounts Issued'
        },
    'Pre-Orders':{
        'labels':['Pre-Order', 'Non Pre-Order'],
        'values':[PreOrder_yes, PreOrder_no],
        'text': 'Pre-Orders<sup>*</sup><sup>*</sup>'
        },
    'Purchase Country':{
        'labels':['CA', 'US'],
        'values':[Country_CA, Country_US],
        'text': 'Purchase Country<sup>*</sup><sup>*</sup>'
        },
    'Purchase Location':{
        'labels':['Online', 'In Store'],
        'values':[Online, Retail_store],
        'text': 'Purchase Location<sup>*</sup><sup>*</sup>'
        }
    }

    labels_1 = pie_chart_dict[dropdown_value_1]['labels']
    values_1 = pie_chart_dict[dropdown_value_1]['values']
    text_1 = pie_chart_dict[dropdown_value_1]['text']
    result_1 = build_piechart(labels_1,values_1,text_1,colors,bgcolor,txcolor)

    return result_1

@app.callback(
    Output('pie_chart_2', 'figure'),
    Input('country_picker_2','value'),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"),
    Input("dropdown_2", "value"),
    Input('intermediate-value', 'children'))
def update_graph(country_2,start_date,end_date,dropdown_value_2, df_json):
    
    df = pd.read_json(df_json, orient='split')

    if 'CA' in country_2:
        CA=True
    else: CA=False
    if 'US' in country_2:
        US=True
    else: US=False

    leather_color_dict,leather_size_dict,knit_color_dict,knit_size_dict,utility_color_dict,utility_size_dict,qty_all_orders,qty_giveaways,Smartfit_order_count,Country_CA,Country_US,PreOrder_yes,PreOrder_no,total_price_sales_usd,total_price_sales_cad,qty_sales_orders,No_Smartfit_order_count,qty_utility_sold,qty_knit_sold,qty_leather_sold,shoes_sold,qty_smartfit_sold,qty_kepler_sold,qty_pascal_sold,qty_giftcard_sold,discount_code_qty_dict,Retail_store,Online=process_df(df,utility_colors,knit_colors,leather_colors,discount_codes_of_interest,CA,US)
    

    pie_chart_dict = {
    'Total Orders':{
        'labels':['Sales', 'Exhanges', 'Give Aways'],
        'values':[qty_sales_orders, discount_code_qty_dict['exchange'], qty_giveaways],
        'text': 'Orders Placed: {}<br> Total Sales USD: {}<br> Total Sales CAD: {}'.format(qty_all_orders,total_price_sales_usd,total_price_sales_cad)
        },
    'Orders with SmartFit':{
        'labels':['Orders with SmartFit', 'Orders without SmartFit'],
        'values':[Smartfit_order_count,  No_Smartfit_order_count],
        'text': 'Sales orders with and without SmartFit<sup>*</sup><sup>*</sup>'
        },
    'Shoe Models Sold':{
        'labels':['Avro Knit', 'Avro Leather', 'Utility'],
        'values':[qty_knit_sold, qty_leather_sold, qty_utility_sold],
        'text': 'Shoes Sold: {}<sup>*</sup><sup>*</sup>'.format(shoes_sold)
        },
    'SmartFit Sold':{
        'labels':['SmartFit'],
        'values':[qty_smartfit_sold],
        'text':'SmartFit Sold<sup>*</sup><sup>*</sup>'
        },
    'Other Products Sold':{
        'labels':['Kepler', 'Pascal', 'Giftcard'],
        'values':[qty_kepler_sold, qty_pascal_sold, qty_giftcard_sold],
        'text': 'Socks and Giftcards Sold<sup>*</sup><sup>*</sup>'
        },
    'Avro Leather Colors':{
        'labels':list(leather_color_dict.keys()),
        'values':list(leather_color_dict.values()),
        'text': 'Avro Leather Colors<sup>*</sup><sup>*</sup>'
        },
    'Avro Leather Genders':{
        'labels':list(leather_size_dict.keys()),
        'values':list(leather_size_dict.values()),
        'text': 'Avro Leather Genders<sup>*</sup><sup>*</sup>'
        },
    'Avro Knit Colors':{
        'labels':list(knit_color_dict.keys()),
        'values':list(knit_color_dict.values()),
        'text': 'Avro Knit Colors<sup>*</sup><sup>*</sup>'
        },
    'Avro Knit Genders':{
        'labels':list(knit_size_dict.keys()),
        'values':list(knit_size_dict.values()),
        'text': 'Avro Knit Genders<sup>*</sup><sup>*</sup>'
        },
    'Avro Utility Colors':{
        'labels':list(utility_color_dict.keys()),
        'values':list(utility_color_dict.values()),
        'text': 'Avro Utility Colors<sup>*</sup><sup>*</sup>'
        },
    'Avro Utility Genders':{
        'labels':list(utility_size_dict.keys()),
        'values':list(utility_size_dict.values()),
        'text': 'Avro Utility Genders<sup>*</sup><sup>*</sup>'
        },
    'Discounts Issued':{
        'labels':list(discount_code_qty_dict.keys()),
        'values':list(discount_code_qty_dict.values()),
        'text': 'Discounts Issued'
        },
    'Pre-Orders':{
        'labels':['Pre-Order', 'Non Pre-Order'],
        'values':[PreOrder_yes, PreOrder_no],
        'text': 'Pre-Orders<sup>*</sup><sup>*</sup>'
        },
    'Purchase Country':{
        'labels':['CA', 'US'],
        'values':[Country_CA, Country_US],
        'text': 'Purchase Country<sup>*</sup><sup>*</sup>'
        },
    'Purchase Location':{
        'labels':['Online', 'In Store'],
        'values':[Online, Retail_store],
        'text': 'Purchase Location<sup>*</sup><sup>*</sup>'
        }
    }

    labels_2 = pie_chart_dict[dropdown_value_2]['labels']
    values_2 = pie_chart_dict[dropdown_value_2]['values']
    text_2 = pie_chart_dict[dropdown_value_2]['text']
    result_2 = build_piechart(labels_2,values_2,text_2,colors,bgcolor,txcolor)

    return result_2

if __name__ == "__main__":
    app.run_server(debug=True, port=8888)