import requests
import json
import pandas as pd
import dateutil.parser as parser
from datetime import datetime, timedelta
import os
import plotly.graph_objs as go

def get_dataframe(start_date,end_date,table_name,engine):

	entire_df = pd.read_sql_table(table_name,con=engine)

	start_date = (parser.parse(start_date)).isoformat()+"-08:00"
	end_date = (parser.parse(end_date)+timedelta(hours=23)+timedelta(minutes=59)+timedelta(seconds=59)).isoformat()+"-08:00"

	reduced_df=entire_df[entire_df['created_at']<=end_date]
	reduced_df=reduced_df[reduced_df['created_at']>=start_date]

	print('start_date',start_date)
	return reduced_df

def process_df(df,utility_colors,knit_colors,leather_colors,discount_codes_of_interest,CA=True,US=True):
    
    if CA == False:
        df = df[df['currency']!='CAD']
    if US == False:
        df = df[df['currency']!='USD']


    # remove time infomrmation from date
    df['created_at'] = pd.to_datetime(df['created_at']).apply(lambda x: x.date())
    
    # How many total_price orders?
    qty_all_orders = len(df)

    #remove exchanges
    df_temp=df[df["discount_code"].str.contains('exchange',na=False,case=False)==False]

    #convert total price to float
    #df_temp['total_price'] = pd.to_numeric(df_temp['total_price'], downcast="float")

    #count free orders and remove free items
    qty_giveaways=len(df_temp[df_temp["total_price"]==0.00])
    df_temp=df_temp[df_temp["total_price"]!=0.00]

    
    df_temp['product']=df_temp['product'].apply(lambda x: x.replace('"',''))
    df_temp['product']=df_temp['product'].apply(lambda x: x.replace('}',''))
    df_temp['product']=df_temp['product'].apply(lambda x: x.replace('{',''))
    df_temp['product']=df_temp['product'].apply(lambda x: x.split(','))
  

    #How many orders have a SmartFit?
    Smartfit_order_count = 0
    for index, row in df_temp.iterrows():
        product_list = row['product']
        if any('SmartFit' in product for product in product_list):
            Smartfit_order_count+=1


     # How many in each country?
    Country_CA = len(df_temp[df_temp['currency']=='CAD'])
    Country_US = len(df_temp[df_temp['currency']=='USD'])
    
    # How many are pre-orders?
    PreOrder_yes=len(df_temp[df_temp['tags']=='pre-order'])
    PreOrder_no=len(df_temp)-PreOrder_yes

    # total_prices sales in $
    df_usd = df_temp[df_temp['currency']=='USD']
    df_cad = df_temp[df_temp['currency']=='CAD']

    total_price_sales_usd = '${:,.2f}'.format(df_usd['total_price'].sum())
    total_price_sales_cad = '${:,.2f}'.format(df_cad['total_price'].sum())

    # How many sales orders?
    qty_sales_orders = len(df_temp)

    # How many sales orders without Smartfit?
    No_Smartfit_order_count = qty_sales_orders-Smartfit_order_count

    # How many of products sold (without exchanges/giveaways)?
    all_products_sold = []
    for index, row in df_temp.iterrows():
        product_list = row['product']
        for item in product_list:
            all_products_sold.append(item)

    # How many of products sold (without exchanges/giveaways)?
    all_products_sold_exchanged_given = []
    for index, row in df.iterrows():
        product_list =  row['product']
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
        discount_code_qty_dict[item]=df['discount_code'].str.contains(str(item), case=False, na=False).sum()

    discount_code_qty_dict['cascacreator']+= df['discount_code'].str.contains('casca creator', case=False, na=False).sum()
    qty_nodiscount = df['discount_code'].isnull().sum()
    discount_code_qty_dict['No Discount'] = qty_nodiscount
    qty_otherdiscount = len(df)-sum(discount_code_qty_dict.values())
    discount_code_qty_dict['Other Discount'] = qty_otherdiscount

    # how many in store?
    Retail_store = len(df_temp[df_temp['location_id']=='15103557690'])
    Online = len(df_temp) - Retail_store

    return leather_color_dict,leather_size_dict,knit_color_dict,knit_size_dict,utility_color_dict,utility_size_dict,qty_all_orders,qty_giveaways,Smartfit_order_count,Country_CA,Country_US,PreOrder_yes,PreOrder_no,total_price_sales_usd,total_price_sales_cad,qty_sales_orders,No_Smartfit_order_count,qty_utility_sold,qty_knit_sold,qty_leather_sold,shoes_sold,qty_smartfit_sold,qty_kepler_sold,qty_pascal_sold,qty_giftcard_sold,discount_code_qty_dict,Retail_store,Online


def build_piechart(labels,values,text,colors,bgcolor,txcolor):

    pie = { #Number of orders
            'data': [go.Pie(labels = labels,
                            values = values,
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
                    'text': text,

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
                    family = "Helvetica,sans-serif",
                    size = 12,
                    color = txcolor)
            ),

        }

    return pie

def get_dataframe_from_shopify(start_date,end_date,CA_key, CA_pass, US_key, US_pass, CA=True,US=True):

	day_before = (parser.parse(start_date)-timedelta(days=1)).isoformat()+"-08:00"
	week_before = (parser.parse(start_date)-timedelta(weeks=1)).isoformat()+"-08:00"

	df_CA = pd.DataFrame()
	df_US = pd.DataFrame()

	start_date = (parser.parse(start_date)).isoformat()+"-08:00"
	end_date = (parser.parse(end_date)+timedelta(hours=23)+timedelta(minutes=59)+timedelta(seconds=59)).isoformat()+"-08:00"

	if CA == True:

		request1 = "https://"+CA_key+":"+CA_pass+"@casca-designs-inc-canada.myshopify.com/admin/api/2021-01/orders.json?limit=1&status=any&fulfillment_status=any&created_at_min="+week_before+"&created_at_max="+day_before+"&fields=name,created_at,id"
		response1 = requests.get(request1)

		id_before =response1.json()['orders'][0]['id']
		print(id_before)

		request = "https://"+CA_key+":"+CA_pass+"@casca-designs-inc-canada.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,location_id,currency,email,fulfillment_status,tags,line_items,discount_applications,shipping_address,total-price,discount_codes"
		response = requests.get(request)

		flag = False
		while flag == False:
			for i in range(len(response.json()['orders'])):
				
				data = {
					'name':[response.json()['orders'][i]['name']],
					'email':[response.json()['orders'][i]['email']],
					'created_at':[response.json()['orders'][i]['created_at']],
					'currency':[response.json()['orders'][i]['currency']],
					'product':[[]],
					'tags':[response.json()['orders'][i]['tags']],
					'id':[int(response.json()['orders'][i]['id'])],
					'location_id':[str(response.json()['orders'][i]['location_id'])],
					'total_price':[response.json()['orders'][i]['total_price']]
					#'fulfillment_status':[response.json()['orders'][i]['fulfillment_status']]
				}
				
				try:
					data['province_code'] = [response.json()['orders'][i]['shipping_address']['province_code']]
				except: data['province_code'] = None
				try:
					data['discount_code']=[response.json()['orders'][i]['discount_codes'][0]['code']]
					data['discount_amount']=[response.json()['orders'][i]['discount_codes'][0]['amount']]
				except:
					data['discount_code']=None
					data['discount_amount']=0
				
				for j in range(len(response.json()['orders'][i]['line_items'])):
					data['product'][0].append(response.json()['orders'][i]['line_items'][j]['name'])
				
				df2 = pd.DataFrame(data=data)
				df_CA = pd.concat([df_CA,df2])

			id_before = df_CA['id'].max()

			request = "https://"+CA_key+":"+CA_pass+"@casca-designs-inc-canada.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,location_id,currency,email,fulfillment_status,tags,line_items,discount_applications,shipping_address,total-price,discount_codes"
			response = requests.get(request)

			if len(response.json()['orders']) == 0:
				flag = True

	if US == True:

		request1 = "https://"+US_key+":"+US_pass+"@casca-designs-inc.myshopify.com/admin/api/2021-01/orders.json?limit=1&status=any&fulfillment_status=any&created_at_min="+week_before+"&created_at_max="+day_before+"&fields=name,created_at,id"
		response1 = requests.get(request1)

		id_before =response1.json()['orders'][0]['id']

		request = "https://"+US_key+":"+US_pass+"@casca-designs-inc.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,location_id,currency,email,fulfillment_status,tags,line_items,discount_applications,shipping_address,total-price,discount_codes"
		response = requests.get(request)
		
		flag = False
		while flag == False:
			
			for i in range(len(response.json()['orders'])):
				data = {
					'name':[response.json()['orders'][i]['name']],
					'email':[response.json()['orders'][i]['email']],
					'created_at':[response.json()['orders'][i]['created_at']],
					'currency':[response.json()['orders'][i]['currency']],
					'product':[[]],
					'tags':[response.json()['orders'][i]['tags']],
					'id':[int(response.json()['orders'][i]['id'])],
					'location_id':[str(response.json()['orders'][i]['location_id'])],
					'total_price':[response.json()['orders'][i]['total_price']]
					#'fulfillment_status':[response.json()['orders'][i]['fulfillment_status']]
				}
				
				try:
					data['province_code'] = [response.json()['orders'][i]['shipping_address']['province_code']]
				except: data['province_code'] = None
				try:
					data['discount_code']=[response.json()['orders'][i]['discount_codes'][0]['code']]
					data['discount_amount']=[response.json()['orders'][i]['discount_codes'][0]['amount']]
				except:
					data['discount_code']=None
					data['discount_amount']=0
				
				for j in range(len(response.json()['orders'][i]['line_items'])):
					data['product'][0].append(response.json()['orders'][i]['line_items'][j]['name'])
				
				df2 = pd.DataFrame(data=data)
				df_US = pd.concat([df_US,df2])

			id_before = df_US['id'].max()

			request = "https://"+US_key+":"+US_pass+"@casca-designs-inc.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,location_id,currency,email,fulfillment_status,tags,line_items,discount_applications,shipping_address,total-price,discount_codes"
			response = requests.get(request)

			if len(response.json()['orders']) == 0:
				flag = True

	df = pd.concat([df_CA,df_US])	
	df=df.reset_index(drop=True)
	
	return df

