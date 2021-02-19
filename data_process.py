from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
import pandas as pd
import dateutil.parser as parser
import os
from datetime import date, timedelta

DB_pass = os.getenv('DB_pass')

URI = 'postgres+psycopg2://ipqektkjozaykv:'+DB_pass+'@ec2-52-7-168-69.compute-1.amazonaws.com:5432/d8d1nqq3e1dfge'
engine = create_engine(URI)

entire_df = pd.read_sql_table('shopifydata',con=engine)

print(entire_df.head)
print(entire_df['created_at'].dtypes)

start_date='2021-01-15'
end_date='2021-02-01'

start_date = (parser.parse(start_date)).isoformat()+"-08:00"
end_date = (parser.parse(end_date)+timedelta(hours=23)+timedelta(minutes=59)+timedelta(seconds=59)).isoformat()+"-08:00"


reduced_df=entire_df[entire_df['created_at']<=end_date]
reduced_df=reduced_df[reduced_df['created_at']>=start_date]

print(reduced_df)