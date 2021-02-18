import psycopg2
from psycopg2 import Error
import pandas as pd
import numpy as np
import json
from pangres import upsert
from sqlalchemy import create_engine, VARCHAR, text

try:
    # Connect to an existing database
    connection = psycopg2.connect(user="postgres",
                                  password="Crooked31",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="casca")

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")
    # Executing a SQL query
    cursor.execute("SELECT version();")
    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

df_orig = pd.read_csv('test.csv')

df_reduced_columns = df_orig[['Name','Email', 'Financial Status','Created at','Total','Discount Code','Discount Amount','Tags','Lineitem quantity','Lineitem name','Lineitem sku','Shipping Province','Payment Method','Accepts Marketing','Location', 'Currency']]
df_reduced_columns = df_reduced_columns[df_reduced_columns['Lineitem name'] != 'Culture Manual']
df_reduced_columns = df_reduced_columns[df_reduced_columns['Lineitem name'] != "The Hitchhiker's Guide to Culture"]

df_reduced_columns['Products Purchased'] = np.empty((len(df_reduced_columns), 0)).tolist()
df_reduced_columns['Purchase Skus'] = np.empty((len(df_reduced_columns), 0)).tolist()
#df_reduced_columns['Products Purchased'] = df_reduced_columns['Products Purchased'].astype('object')
#df_reduced_columns['Purchase Skus'] = df_reduced_columns['Purchase Skus'].astype('object')

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

#df['Products Purchased'] = 'one'
#df['Purchase Skus'] = 'two'

#df.set_index('Name', inplace=True)

dtype = {'Name':VARCHAR(50)}

##print(df.columns)

engine = create_engine("postgresql+psycopg2://{user}:{pw}@127.0.0.1/{db}".format(user="postgres", pw="Crooked31",db="casca"))

d={'customer_id':['1','2','3'],'name':['IMB','Microsoft','intel'],'email':['tim@bob.com','bill@jim.com','ted@sam.com']}
df=pd.DataFrame(data=d)

query = text(f""" 
                DROP TABLE IF EXISTS customers;

				CREATE TABLE customers (
					customer_id serial PRIMARY KEY,
					name VARCHAR UNIQUE,
					email VARCHAR NOT NULL,
					active bool NOT NULL DEFAULT TRUE
				);

				INSERT INTO customers (customer_id, name, email)
				VALUES {','.join([str(i) for i in list(df.to_records(index=False))])} 
				ON CONFLICT (customer_id) 
				DO 
   					UPDATE SET customer_id = EXCLUDED.customer_id, email = EXCLUDED.email, name = EXCLUDED.name;
         """)

engine.execute(query)

# Insert whole DataFrame into MySQL
#upsert(engine=engine, df=df, table_name='shopify_data', if_row_exists='update',dtype=dtype)