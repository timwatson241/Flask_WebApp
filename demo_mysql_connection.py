import pandas as pd

# Create dataframe
data=pd.DataFrame({
    'book_id':[12345,12346,12347],
    'title':['Python Programming','Learn MySQL','Data Science Cookbook'],
    'price':[29,23,27]
})

from sqlalchemy import create_engine

# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                       .format(user="root",
                               pw="Crooked31!",
                               db="csvData"))

# Insert whole DataFrame into MySQL
data.to_sql('book_details', con = engine, if_exists = 'append', chunksize = 1000)