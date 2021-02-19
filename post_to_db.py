from helpers import get_dataframe
import os
from datetime import date, timedelta
#import dateutil.parser as parser
#import requests
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

# Shopify API credentials
CA_key = os.getenv('CA_key')
CA_pass = os.environ.get('CA_pass')

US_key = os.getenv('US_key')
US_pass = os.environ.get('US_pass')

DB_pass = os.getenv('DB_pass') #153c017c2d44caa6396d985f693586a4b89241fee050e6e06f5cd3f040234a68

start_date = date(2021, 1, 1).strftime("%Y-%m-%dT23:59:59")
end_date = date.today().strftime("%Y-%m-%dT23:59:59")

URI = 'postgres+psycopg2://ipqektkjozaykv:'+DB_pass+'@ec2-52-7-168-69.compute-1.amazonaws.com:5432/d8d1nqq3e1dfge'
engine = create_engine(URI, echo = True)

df = get_dataframe(start_date,end_date,CA_key, CA_pass, US_key, US_pass, CA=True,US=True)

df.to_sql('shopifydata', con=engine, if_exists='replace')

