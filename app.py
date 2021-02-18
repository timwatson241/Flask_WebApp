import base64
import os
from urllib.parse import quote as urlquote
import datetime
from datetime import date
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from sqlalchemy import create_engine, VARCHAR, text
import numpy as np
import json
from pangres import upsert
import plotly.graph_objs as go
import plotly.express as px
from datetime import timedelta
import dash_table
import sqlalchemy
from sqlalchemy.dialects.postgresql import insert
import psycopg2

UPLOAD_DIRECTORY = './upload_dir/'#+datetime.datetime.now().strftime("%d%m%y%H")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(server=server)

engine = create_engine("postgresql+psycopg2://{user}:{pw}@127.0.0.1/{db}".format(user="postgres", pw="Crooked31",db="casca"))

global table_name
table_name = 'shopifydata1'

global bgcolor
bgcolor = '#000'

global txcolor
txcolor = '#ebebeb'

global df
df = pd.read_sql_table(table_name, engine)

global utility_colors
utility_colors = ['Aluminum', 'Black']
global knit_colors
knit_colors = ['Space Black', 'Ash White', 'Black', 'Clay Blue', 'Light Grey', 'Wine', 'Moss', 'Charcoal']
global leather_colors
leather_colors = ['Light Grey', 'Black', 'Ceramic White', 'White/Gum', 'Titanium', 'Sand', 'Space Black', 'Navy Suede']

global discount_codes_of_interest
discount_codes_of_interest = ['exchange','braden','warranty','cascacreator','error','endlessflight']

@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

app.layout = html.Div(
    [
        html.H1("Casca sales data analyzer", style={"textAlign": "center",'color':txcolor, 'margin-top':'-5px','font-size':'60px'}),
        
        html.H2("Step #1: Upload new csv data", style={'textAlign':'center','color':txcolor}),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Upload new data by dragging and dropping or clicking here"]
            ),
            style={
                "width": "60%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                #"margin": "30px",
                'color':bgcolor,
                'backgroundColor': '#F8BF14',
                'margin':'0 auto',
                'display':'block'

            },
            multiple=True,
        ),
        html.H2("Step #2: Pick the date range you would like to analyze", style={'textAlign':'center','color':txcolor}),
        html.H4(id='dates-available', style={'textAlign':'center','color':txcolor}),
        dcc.DatePickerRange(
                        id='date_range',
                        day_size = 50,
                        reopen_calendar_on_clear=True,
                        clearable = True,
                        min_date_allowed = df['Created at datetime'].min(),
                        max_date_allowed = df['Created at datetime'].max(),
                        # initial_visible_month = date(2020, 7, 1),
                        start_date = date(2021, 1, 1),
                        end_date = date(2021, 1, 30),
                        minimum_nights = 0,
                        updatemode = 'singledate',
                        className = 'dcc_compon',
                        style={'display':'flex', 'justifyContent':'center', 'margin-bottom':'15px','color':txcolor}),
        
        dcc.Checklist(
        id='country_picker',
        options=[
            {'label': 'Canada', 'value': 'CA'},
            {'label': 'USA', 'value': 'US'}
        ],
        value=['CA', 'US'],
        style={'display':'flex', 'justifyContent':'center', 'margin-bottom':'15px','color':txcolor}),

        html.Div([
            html.Div([
                dcc.Graph(id = 'pie_chart_orderqty',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_smartfit_orders',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_shoenumbers',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'33%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_smartfitnumbers',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'33%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_socknumbers',
                          config = {'displayModeBar': 'hover'}),

            ],style={'width':'33%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_leathercolors',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_leathersizes',
                          config = {'displayModeBar': 'hover'}),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_knitcolors',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_knitsizes',
                          config = {'displayModeBar': 'hover'}),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_utilitycolors',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_utilitysizes',
                          config = {'displayModeBar': 'hover'}),

            ],style={'width':'50%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_discounts',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'100%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_preorder',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'33%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_country',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'33%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'pie_chart_instore',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'33%','display':'inline-block'}),
            html.Div([
                dcc.Graph(id = 'bar-chart',
                          config = {'displayModeBar': 'hover'},),

            ],style={'width':'100%','display':'inline-block'})]),

        html.H2("Data",style={'textAlign':'center','color':txcolor}),
        html.Div([
                dash_table.DataTable(id='table'),
            ],style={'width':'100%','display':'inline-block'}),
        html.H2("File List",style={'color':txcolor}),
        html.Ul(id="file-list",style={'color':txcolor})
    ],
    style={"background-color": bgcolor},
)


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    UPLOAD_PATH = UPLOAD_DIRECTORY
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)
    with open(os.path.join(UPLOAD_PATH, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


DATABASE_COLUMNS = ['Name', 'Email', 'Financial Status', 'Total', 'Discount Code', 'Discount Amount', 'Tags', 'Shipping Province', 'Payment Method', 'Accepts Marketing', 'Location', 'Products Purchased', 'Purchase Skus', 'Country', 'Created at datetime']
PRIMARY_KEY = 'Name'

def create_update_query(table):
    """This function creates an upsert query which replaces existing data based on primary key conflicts"""
    columns = ', '.join([f'{col}' for col in DATABASE_COLUMNS])
    #constraint = ', '.join([f'{col}' for col in PRIMARY_KEY])
    placeholder = ', '.join([f'%({col})s' for col in DATABASE_COLUMNS])
    updates = ', '.join([f'{col} = EXCLUDED.{col}' for col in DATABASE_COLUMNS])
    query = f"""INSERT INTO {table} ({columns}) 
                VALUES ({placeholder}) 
                ON CONFLICT ('Email') 
                DO UPDATE SET {updates};"""
    query.split()
    query = ' '.join(query.split())
    return query


def load_updates(df, table, connection):
    conn = connection.get_conn()
    cursor = conn.cursor()
    df1 = df.where((pd.notnull(df)), None)
    insert_values = df1.to_dict(orient='records')
    for row in insert_values:
        cursor.execute(create_update_query(table=table), row)
        conn.commit()
    row_count = len(insert_values)
    logging.info(f'Inserted {row_count} rows.')
    cursor.close()
    del cursor
    conn.close()

def parseCSV(filePath):
      # CVS Column Names
      #col_names = ['first_name','last_name','address', 'street', 'state' , 'zip']
      # Use Pandas to parse the CSV file
      df_orig = pd.read_csv(filePath)


      df_reduced_columns = df_orig[['Name','Email', 'Financial Status','Created at','Total','Discount Code','Discount Amount','Tags','Lineitem quantity','Lineitem name','Lineitem sku','Shipping Province','Payment Method','Accepts Marketing','Location', 'Currency']]
      df_reduced_columns = df_reduced_columns[df_reduced_columns['Lineitem name'] != 'Culture Manual']
      df_reduced_columns = df_reduced_columns[df_reduced_columns['Lineitem name'] != "The Hitchhiker's Guide to Culture"]
  
      df_reduced_columns['Products Purchased'] = np.empty((len(df_reduced_columns), 0)).tolist()
      df_reduced_columns['Purchase Skus'] = np.empty((len(df_reduced_columns), 0)).tolist()
      df_reduced_columns['Products Purchased'] = df_reduced_columns['Products Purchased'].astype('object')
      df_reduced_columns['Purchase Skus'] = df_reduced_columns['Purchase Skus'].astype('object')

      df_reduced_columns['remove']=''
      df_reduced_columns['Country']=''

      df_reduced_columns['Country'] = np.where(df_reduced_columns['Currency'].str.contains("USD", na=False), 'US', 'CA')

      Email = None
      for index, row in df_reduced_columns.iterrows():
          for a in range(row['Lineitem quantity']):
              row['Products Purchased'].append(row['Lineitem name'])
              row['Purchase Skus'].append(row['Lineitem sku'])
          if row['Email']==Email:
              i+=1
              df_reduced_columns.loc[index, 'remove'] = 'Yes'
              for b in range(row['Lineitem quantity']):
                  df_reduced_columns.loc[index-i,'Products Purchased'].append(row['Lineitem name'])
                  df_reduced_columns.loc[index-i,'Purchase Skus'].append(row['Lineitem sku'])
              
          else: i = 0
          Email = row['Email']

      df = df_reduced_columns[df_reduced_columns['remove'] != 'Yes']

      df['Created at datetime'] = pd.to_datetime(df['Created at'],format='%m/%d/%y %H:%M')
      df = df.drop(columns=['remove','Lineitem name','Lineitem sku','Created at','Lineitem quantity','Currency'])
      df['Location'] = df['Location'].replace(np.nan, 'Online')

      df['Products Purchased'] = df['Products Purchased'].apply(json.dumps)
      df['Purchase Skus'] = df['Purchase Skus'].apply(json.dumps)

      #df.set_index('Name', inplace=True)

      #dtype = {'Name':VARCHAR(50)}

      connection = psycopg2.connect(user="postgres",
                                  password="Crooked31",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="casca")

      
      query = create_update_query(table_name)

      print(query)
      engine.execute(query)

      #load_updates(df, table_name, connection)
   
      # Insert whole DataFrame into MySQL
      '''new_df.to_sql(
        table_name, 
        con=engine,  
        if_exists='replace'
        )'''


      ### NOW WE HAVE TO RECALCULATE ALL THE VARIABLES

def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output("file-list", "children"),
    Output("date_range", "min_date_allowed"),
    Output("date_range", "max_date_allowed"),
    Output("dates-available", "children"),
    Output("date_range", "start_date"),
    Output("date_range", "end_date"),
    Input("upload-data", "filename"),
    Input("upload-data", "contents"))
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            name = datetime.datetime.now().strftime("%d%m%y%H")+"_"+name
            save_file(name, data)
            parseCSV(os.path.join(UPLOAD_DIRECTORY, name))
            global df
            df = pd.read_sql_table(table_name, engine)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")], df['Created at datetime'].min(), df['Created at datetime'].max(), "Data exists from {} to {}".format(df['Created at datetime'].min(), df['Created at datetime'].max()),df['Created at datetime'].min(), df['Created at datetime'].max()
    else:
        return [html.Li(file_download_link(filename)) for filename in files if filename != '.DS_Store'], df['Created at datetime'].min(), df['Created at datetime'].max(),"Data exists from {} to {}".format(df['Created at datetime'].min(), df['Created at datetime'].max()),df['Created at datetime'].min(), df['Created at datetime'].max()

@app.callback(
    Output('pie_chart_orderqty', 'figure'),
    Output('pie_chart_smartfit_orders', 'figure'),
    Output('pie_chart_shoenumbers', 'figure'),
    Output('pie_chart_smartfitnumbers', 'figure'),
    Output('pie_chart_socknumbers', 'figure'),
    Output('pie_chart_leathercolors', 'figure'),
    Output('pie_chart_leathersizes', 'figure'),
    Output('pie_chart_knitcolors', 'figure'),
    Output('pie_chart_knitsizes', 'figure'),
    Output('pie_chart_utilitycolors', 'figure'),
    Output('pie_chart_utilitysizes', 'figure'),
    Output('pie_chart_discounts', 'figure'),
    Output('pie_chart_preorder', 'figure'),
    Output('pie_chart_country', 'figure'),
    Output('pie_chart_instore', 'figure'),
    Output("bar-chart", "figure"),
    Output("table", "columns"),
    Output("table", "data"),
    Output("table", "style_table"),
    Output("table", "style_cell"),
    Output("table", "tooltip_data"),
    Output("table", "page_size"),
    Output("table", "style_cell_conditional"),
    Input('country_picker','value'),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"),
    Input("file-list", "children"))
def update_graph(country,start_date,end_date,filelist):
    
    df = pd.read_sql_table(table_name, engine)


    # Filter dataframe by country
    df= df[df['Country'].isin(country)]

    df['Created at datetime'] = pd.to_datetime(df['Created at datetime']).apply(lambda x: x.date())

    # Filter dataframe by start/end date
    
    df = df[df['Created at datetime']>= pd.to_datetime(start_date,format='%Y-%m-%d')]
    df = df[df['Created at datetime']<= pd.to_datetime(end_date,format='%Y-%m-%d')+timedelta(days=1)]
    
    # How many total orders?
    qty_all_orders = len(df)

        #remove exchanges
    df_temp=df[df["Discount Code"].str.contains('exchange',na=False,case=False)==False]

        #remove free items
    df_temp=df_temp[df_temp["Total"]!=0]

    #How many orders have a SmartFit?
    Smartfit_order_count = 0
    for index, row in df_temp.iterrows():
        product_list = json.loads(row['Products Purchased'])
        if any('SmartFit' in product for product in product_list):
            Smartfit_order_count+=1

     # How many in each country?
    Country_CA = len(df_temp[df_temp['Country']=='CA'])
    Country_US = len(df_temp[df_temp['Country']=='US'])
    
    # How many are pre-orders?
    PreOrder_yes=len(df_temp[df_temp['Tags']=='pre-order'])
    PreOrder_no=len(df_temp)-PreOrder_yes

    # Totals sales in $
    df_usd = df_temp[df_temp['Country']=='US']
    df_cad = df_temp[df_temp['Country']=='CA']
    total_sales_usd = '${:,.2f}'.format(df_usd['Total'].sum())
    total_sales_cad = '${:,.2f}'.format(df_cad['Total'].sum())

    # calculate giveaways
    df_new = df[df['Total']==0]
    df_new=df_new[df_new['Discount Code'].str.contains('exchange',na=False,case=False)==False]

    qty_giveaways=len(df_new)

    # How many sales orders?
    qty_sales_orders = len(df_temp)

    # How many sales orders without Smartfit?
    No_Smartfit_order_count = qty_sales_orders-Smartfit_order_count

    # Whate states are customers in?
    states_dict = {}
    for index, row in df_temp.iterrows():
        if row['Shipping Province'] != None:
            if row['Shipping Province'] in states_dict:
                states_dict[row['Shipping Province']]+=1
            else: states_dict[row['Shipping Province']] = 1

    states_df = pd.DataFrame({'state':list(states_dict.keys()),'number of orders':list(states_dict.values())})
    states_df['Color']='#a99e8d'
    canada=['AB','BC','SK','MB','ON','QC','NL','NB','NS','PE','YK','NT','NU']
    for index, row in states_df.iterrows():
        if row['state'] in canada:
            states_df['Color'][index]= 'red'

    # How many of products sold (without exchanges/giveaways)?
    all_products_sold = []
    for index, row in df_temp.iterrows():
        product_list = json.loads(row['Products Purchased'])
        for item in product_list:
            all_products_sold.append(item)

    # How many of products sold (without exchanges/giveaways)?
    all_products_sold_exchanged_given = []
    for index, row in df.iterrows():
        product_list = json.loads(row['Products Purchased'])
        for item in product_list:
            all_products_sold_exchanged_given.append(item)

    # how many utility
    Utility_list_all_sizes = []
    for item in all_products_sold:
        if 'Utility' in item:
            Utility_list_all_sizes.append(item)

    qty_utility_sold = len(Utility_list_all_sizes)

    # How many of each color - utility
    utility_color_dict={}
    for color in utility_colors:
        utility_color_dict[color]=0
        for item in Utility_list_all_sizes:
            if color in item:
                utility_color_dict[color]+=1


    # How many men's/Women's utility
    utility_size_dict = {"Mens":0,"Womens":0}
    for item in Utility_list_all_sizes:
        size = item.split('Mens')[1][1:5]
        size = size.replace(" ","")
        size = size.replace("/","")
        size=float(size)
        if size > 8:
            utility_size_dict["Mens"]+=1
        else:utility_size_dict["Womens"]+=1

    # How many knit
    AvroKnit_list_all_sizes = []
    for item in all_products_sold:
        if 'Knit' in item:
            AvroKnit_list_all_sizes.append(item)

    #print(AvroKnit_list_all_sizes)

    qty_knit_sold = len(AvroKnit_list_all_sizes)

    # How many of each color - Knit
    knit_color_dict={}
    for color in knit_colors:
        knit_color_dict[color]=0
        for item in AvroKnit_list_all_sizes:
            if color != 'Black':
                if color in item:
                    knit_color_dict[color]+=1
            else:
                if color in item and "Space Black" not in item:
                    knit_color_dict[color]+=1

    # How many men's/Women's knit
    knit_size_dict = {"Mens":0,"Womens":0}
    for item in AvroKnit_list_all_sizes:
        size = item.split('Mens')[1][1:5]
        size = size.replace(" ","")
        size = size.replace("/","")
        size=float(size)
        if size > 8:
            knit_size_dict["Mens"]+=1
        else:knit_size_dict["Womens"]+=1

    # How many Leather
    AvroLeather_list_all_sizes = []
    for item in all_products_sold:
        if 'Leather' in item:
            AvroLeather_list_all_sizes.append(item)

    qty_leather_sold = len(AvroLeather_list_all_sizes)

    shoes_sold = qty_leather_sold+qty_knit_sold+qty_utility_sold

    # How many of each color - Leather
    leather_color_dict={}
    for color in leather_colors:
        leather_color_dict[color]=0
        for item in AvroLeather_list_all_sizes:
            if color != 'Black':
                if color in item:
                    leather_color_dict[color]+=1
            else:
                if color in item and "Space Black" not in item:
                    leather_color_dict[color]+=1

    # How many men's/Women's leather
    leather_size_dict = {"Mens":0,"Womens":0}
    for item in AvroLeather_list_all_sizes:
        size = item.split('Mens')[1][1:5]
        size = size.replace(" ","")
        size = size.replace("/","")
        size=float(size)
        if size > 8:
            leather_size_dict["Mens"]+=1
        else:leather_size_dict["Womens"]+=1

    #How many Smartfit
    SmartFit_list= []
    for item in all_products_sold:
        if 'SmartFit' in item:
            SmartFit_list.append(item)
        elif 'FootB' in item:
            SmartFit_list.append(item)

    qty_smartfit_sold = len(SmartFit_list)

    #How many Kepler
    Kelper_list_all_sizes= []
    for item in all_products_sold:
        if 'Kepler' in item:
            Kelper_list_all_sizes.append(item)

    qty_kepler_sold = len(Kelper_list_all_sizes)

    #How many Pascal
    Pascal_list_all_sizes= []
    for item in all_products_sold:
        if 'Pascal' in item:
            Pascal_list_all_sizes.append(item)

    qty_pascal_sold = len(Pascal_list_all_sizes)

    #Many Gift card
    Giftcard_list_all_sizes= []
    for item in all_products_sold:
        if 'Gift' in item:
            Giftcard_list_all_sizes.append(item)

    qty_giftcard_sold = len(Giftcard_list_all_sizes)

    #How many have discounts
    discount_code_qty_dict={}
    for item in discount_codes_of_interest:
        discount_code_qty_dict[item]=df['Discount Code'].str.contains(str(item), case=False, na=False).sum()

    discount_code_qty_dict['cascacreator']+= df['Discount Code'].str.contains('casca creator', case=False, na=False).sum()
    qty_nodiscount = df['Discount Code'].isnull().sum()
    discount_code_qty_dict['No Discount'] = qty_nodiscount
    qty_otherdiscount = len(df)-sum(discount_code_qty_dict.values())
    discount_code_qty_dict['Other Discount'] = qty_otherdiscount

    # how many in store?
    Retail_store = len(df_temp[df_temp['Location']=='Casca Designs Retail Store'])
    Online = len(df_temp[df_temp['Location']=='Online'])

    colors = ['#F8BF14','#ebebeb', '#a99e8d','#ffffff','#2a2b2c','#94a9af','#4e75d4','#ffbb00']


    return { #Number of orders
        'data': [go.Pie(labels = ['Sales', 'Exhanges', 'Give Aways'],
                        values = [qty_sales_orders, discount_code_qty_dict['exchange'], qty_giveaways],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 90
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Total Orders Placed: {}<br> Total Sales USD: {}<br> Total Sales CAD: {}'.format(qty_all_orders,total_sales_usd,total_sales_cad),

                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},

            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #Number of orders
        'data': [go.Pie(labels = ['Orders with SmartFit', 'Orders without SmartFit'],
                        values = [Smartfit_order_count,  No_Smartfit_order_count],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 90
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Sales orders with and without SmartFit<sup>*</sup><sup>*</sup>',

                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},

            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #Shoe types sold
        'data': [go.Pie(labels = ['Avro Knit', 'Avro Leather', 'Utility'],
                        values = [qty_knit_sold, qty_leather_sold, qty_utility_sold],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 60
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Total Shoes Sold: {}<sup>*</sup><sup>*</sup>'.format(shoes_sold),

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},

            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #Smartfit sold
        'data': [go.Pie(labels = ['SmartFit'],
                        values = [qty_smartfit_sold],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 60
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'SmartFit Sold<sup>*</sup><sup>*</sup>',

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #Sock types sold
        'data': [go.Pie(labels = ['Kepler', 'Pascal', 'Giftcard'],
                        values = [qty_kepler_sold, qty_pascal_sold, qty_giftcard_sold],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 60
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Socks and Giftcards Sold<sup>*</sup><sup>*</sup>',

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #leather colors
        'data': [go.Pie(labels = list(leather_color_dict.keys()),
                        values = list(leather_color_dict.values()),
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 60
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Avro Leather Colors<sup>*</sup><sup>*</sup>',

                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.2},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #leather sizes
        'data': [go.Pie(labels = list(leather_size_dict.keys()),
                        values = list(leather_size_dict.values()),
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 60
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Avro Leather Genders<sup>*</sup><sup>*</sup>',

                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #knit colors
        'data': [go.Pie(labels = list(knit_color_dict.keys()),
                        values = list(knit_color_dict.values()),
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 130
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Avro Knit Colors<sup>*</sup><sup>*</sup>',

                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.2},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #knit size
        'data': [go.Pie(labels = list(knit_size_dict.keys()),
                        values = list(knit_size_dict.values()),
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 60
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Avro Knit Genders<sup>*</sup><sup>*</sup>',

                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #utility colors
        'data': [go.Pie(labels = list(utility_color_dict.keys()),
                        values = list(utility_color_dict.values()),
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 90
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Avro Utility Colors<sup>*</sup><sup>*</sup>',

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #utility sizes
        'data': [go.Pie(labels = list(utility_size_dict.keys()),
                        values = list(utility_size_dict.values()),
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 60
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Avro Utility Genders<sup>*</sup><sup>*</sup>',

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ # what discounts
        'data': [go.Pie(labels = list(discount_code_qty_dict.keys()),
                        values = list(discount_code_qty_dict.values()),
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 190
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Discounts Issued',

                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.2},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ #Pre-order or no
        'data': [go.Pie(labels = ['Pre-Order', 'Non Pre-Order'],
                        values = [PreOrder_yes, PreOrder_no],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 220
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Pre-Orders<sup>*</sup><sup>*</sup>',

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ # what country
        'data': [go.Pie(labels = ['CA', 'US'],
                        values = [Country_CA, Country_US],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'inside',
                        # hole = .7,
                        rotation = 220
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Purchase Country<sup>*</sup><sup>*</sup>',

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ # in store?
        'data': [go.Pie(labels = ['Online', 'In Store'],
                        values = [Online, Retail_store],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'auto',
                        # hole = .7,
                        rotation = 220
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            #width=800,
            #height=520,
            plot_bgcolor = bgcolor,
            paper_bgcolor = bgcolor,
            hovermode = 'x',
            title = {
                'text': 'Purchase Location<sup>*</sup><sup>*</sup>',

                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': txcolor,
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': bgcolor,
                'xanchor': 'center', 'x': 0.5, 'y': -0.05},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = txcolor)
        ),

    },{ # in store?
        'data': [go.Bar(x= states_df['state'],#list(states_dict.keys()),
                        y = states_df['number of orders'],
                        textposition = 'auto',
                        marker={'color':states_df['Color']})
        ],

        'layout': go.Layout(
            titlefont = {
                'color': txcolor,
                'size': 15},
            title = {
                'text': 'Purchase Province/State<sup>*</sup><sup>*</sup>',

                'y': 0.85,
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
            #width = 10000,
            plot_bgcolor = '#ebebeb',
            paper_bgcolor = bgcolor
        ),

    },[ # Table Properties
        {"name": i, "id": i} for i in df.columns
    ],(
        df.to_dict('records')
    ),{
        'overflowX': 'auto','Width':'100%','Height':'50px'
    },{ 
        'width': 'auto','maxWidth':'50px','overflow': 'hidden','textOverflow': 'ellipsis'
    },[
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df.to_dict('records')
    ],(
        10
    ),[
        {'if': {'column_id': 'Name'},
         'width': '120px'},
    ]

if __name__ == "__main__":
    app.run_server(debug=True, port=8888)