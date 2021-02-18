import requests
import json
import pandas as pd
import dateutil.parser as parser
from datetime import datetime, timedelta
import os

# Get environment variables
CA_key = os.getenv('CA_key')
CA_pass = os.environ.get('CA_pass')

US_key = os.getenv('US_key')
US_pass = os.environ.get('US_pass')

def get_dataframe(start_date,end_date,CA=True,US=True):

	day_before = (parser.parse(start_date)-timedelta(days=1)).isoformat()
	week_before = (parser.parse(start_date)-timedelta(weeks=1)).isoformat()

	df_CA = pd.DataFrame()
	df_US = pd.DataFrame()

	if CA == True:

		request1 = "https://"+CA_key+":"+CA_pass+"@casca-designs-inc-canada.myshopify.com/admin/api/2021-01/orders.json?limit=1&status=any&fulfillment_status=any&created_at_min="+week_before+"&created_at_max="+day_before+"&fields=name,created_at,id,currency,email,fulfillment_status,tags,line_items,discount_applications,id,total-price,discount_codes"
		response1 = requests.get(request1)

		id_before =response1.json()['orders'][0]['id']

		request = "https://"+CA_key+":"+CA_pass+"@casca-designs-inc-canada.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,currency,email,fulfillment_status,tags,line_items,discount_applications,id,total-price,discount_codes"
		response = requests.get(request)

		flag = False
		while flag == False:
			for i in range(len(response.json()['orders'])):
				try:
					data = {
						'name':[response.json()['orders'][i]['name']],
						'email':[response.json()['orders'][i]['email']],
						'created_at':[response.json()['orders'][i]['created_at']],
						'currency':[response.json()['orders'][i]['currency']],
						'discount_code':[response.json()['orders'][i]['discount_codes'][0]['code']],
						'discount_amount':[response.json()['orders'][i]['discount_codes'][0]['amount']],
						'product':[[]],
						'tags':[response.json()['orders'][i]['tags']],
						'id':[response.json()['orders'][i]['id']],
						'total_price':[response.json()['orders'][i]['total_price']]
						#'fulfillment_status':[response.json()['orders'][i]['fulfillment_status']]
					}
				except:
					data = {
						'name':[response.json()['orders'][i]['name']],
						'email':[response.json()['orders'][i]['email']],
						'created_at':[response.json()['orders'][i]['created_at']],
						'currency':[response.json()['orders'][i]['currency']],
						'discount_code':None,
						'discount_amount':0,
						'product':[[]],
						'tags':[response.json()['orders'][i]['tags']],
						'id':[response.json()['orders'][i]['id']],
						'total_price':[response.json()['orders'][i]['total_price']]
						#'fulfillment_status':[response.json()['orders'][i]['fulfillment_status']]
					}
				
				for j in range(len(response.json()['orders'][i]['line_items'])):
					data['product'][0].append(response.json()['orders'][i]['line_items'][j]['name'])
				
				df2 = pd.DataFrame(data=data)
				df_CA = pd.concat([df_CA,df2])

			id_before = df_CA['id'].max()

			request = "https://"+CA_key+":"+CA_pass+"@casca-designs-inc-canada.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,currency,email,fulfillment_status,tags,line_items,discount_applications,id,total-price,discount_codes"
			response = requests.get(request)

			if len(response.json()['orders']) == 0:
				flag = True

	if US == True:

		request1 = "https://"+US_key+":"+US_pass+"@casca-designs-inc.myshopify.com/admin/api/2021-01/orders.json?limit=1&status=any&fulfillment_status=any&created_at_min="+week_before+"&created_at_max="+day_before+"&fields=name,created_at,id,currency,email,fulfillment_status,tags,line_items,discount_applications,id,total-price,discount_codes"
		response1 = requests.get(request1)

		id_before =response1.json()['orders'][0]['id']

		request = "https://"+US_key+":"+US_pass+"@casca-designs-inc.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,currency,email,fulfillment_status,tags,line_items,discount_applications,id,total-price,discount_codes"
		response = requests.get(request)
		
		flag = False
		while flag == False:
			
			for i in range(len(response.json()['orders'])):
				try:
					data = {
						'name':[response.json()['orders'][i]['name']],
						'email':[response.json()['orders'][i]['email']],
						'created_at':[response.json()['orders'][i]['created_at']],
						'currency':[response.json()['orders'][i]['currency']],
						'discount_code':[response.json()['orders'][i]['discount_codes'][0]['code']],
						'discount_amount':[response.json()['orders'][i]['discount_codes'][0]['amount']],
						'product':[[]],
						'tags':[response.json()['orders'][i]['tags']],
						'id':[response.json()['orders'][i]['id']],
						'total_price':[response.json()['orders'][i]['total_price']]
						#'fulfillment_status':[response.json()['orders'][i]['fulfillment_status']]
					}
				except:
					data = {
						'name':[response.json()['orders'][i]['name']],
						'email':[response.json()['orders'][i]['email']],
						'created_at':[response.json()['orders'][i]['created_at']],
						'currency':[response.json()['orders'][i]['currency']],
						'discount_code':None,
						'discount_amount':0,
						'product':[[]],
						'tags':[response.json()['orders'][i]['tags']],
						'id':[response.json()['orders'][i]['id']],
						'total_price':[response.json()['orders'][i]['total_price']]
						#'fulfillment_status':[response.json()['orders'][i]['fulfillment_status']]
					}
				
				for j in range(len(response.json()['orders'][i]['line_items'])):
					data['product'][0].append(response.json()['orders'][i]['line_items'][j]['name'])
				
				df2 = pd.DataFrame(data=data)
				df_US = pd.concat([df_US,df2])

			id_before = df_US['id'].max()

			request = "https://"+US_key+":"+US_pass+"@casca-designs-inc.myshopify.com/admin/api/2021-01/orders.json?limit=50&status=any&since_id="+str(id_before)+"&fulfillment_status=any&created_at_min="+start_date+"&created_at_max="+end_date+"&fields=name,created_at,id,currency,email,fulfillment_status,tags,line_items,discount_applications,id,total-price,discount_codes"
			response = requests.get(request)

			if len(response.json()['orders']) == 0:
				flag = True

	df = pd.concat([df_CA,df_US])	
	df=df.reset_index(drop=True)
	
	return df

start_date = '2021-01-01T00:00:00-08:00'
end_date = '2021-01-31T23:59:59-08:00'

df = get_dataframe(start_date, end_date, CA=False)
df.to_csv('output.csv')

print(df)
