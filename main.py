from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_session import Session
import os
from os.path import join, dirname, realpath
import os
import datetime
import subprocess
from subprocess import check_output
from werkzeug.utils import secure_filename
import pandas as pd
from sqlalchemy import create_engine, VARCHAR
import numpy as np
import json
from pangres import upsert

app = Flask(__name__)
app.secret_key = b'_5#e2L"F4fr8z47fb739nxec]skllfniasgfffsd/'

# enable debugging mode
app.config["DEBUG"] = True

# create sqlalchemy engine
#engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root", pw="Crooked31!",db="casca"))

ALLOWED_EXTENSIONS = set(['csv'])

def CreateNewDir():
    print("I am being called")
    global UPLOAD_FOLDER
    print(UPLOAD_FOLDER)
    UPLOAD_FOLDER = UPLOAD_FOLDER+datetime.datetime.now().strftime("%d%m%y%H")
    cmd="mkdir -p %s && ls -lrt %s"%(UPLOAD_FOLDER,UPLOAD_FOLDER)
    process = subprocess.Popen([cmd], shell=True,  stdout = subprocess.PIPE)
    output, err = process.communicate()
    output = output.decode("utf-8")
    print(output)
    if "total 0" in output:
        print("Success: Created Directory %s"%(UPLOAD_FOLDER)) 
    elif "total" in output:
        print("Failure: Failed to Create a Directory (or) Directory already Exists",UPLOAD_FOLDER)
    else:
        print("Success: Created Directory %s"%(UPLOAD_FOLDER)) 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            global UPLOAD_FOLDER
            UPLOAD_FOLDER = './upload_dir/'
            CreateNewDir()
            #global UPLOAD_FOLDER
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            parseCSV(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('index.html')   

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
      df_reduced_columns['Products Purchased'] = df_reduced_columns['Product(s) Purchased'].astype('object')
      df_reduced_columns['Purchase Skus'] = df_reduced_columns['Purchase Sku(s)'].astype('object')

      df_reduced_columns['remove']=''
      df_reduced_columns['Country']=''

      df_reduced_columns['Country'] = np.where(df_reduced_columns['Currency'].str.contains("USD", na=False), 'US', 'CA')

      Email = None
      for index, row in df_reduced_columns.iterrows():
          for a in range(row['Lineitem quantity']):
              row['Product(s) Purchased'].append(row['Lineitem name'])
              row['Purchase Sku(s)'].append(row['Lineitem sku'])
          if row['Email']==Email:
              i+=1
              df_reduced_columns.loc[index, 'remove'] = 'Yes'
              for b in range(row['Lineitem quantity']):
                  df_reduced_columns.loc[index-i,'Product(s) Purchased'].append(row['Lineitem name'])
                  df_reduced_columns.loc[index-i,'Purchase Sku(s)'].append(row['Lineitem sku'])
              
          else: i = 0
          Email = row['Email']

      df = df_reduced_columns[df_reduced_columns['remove'] != 'Yes']

      df['Created at datetime'] = pd.to_datetime(df['Created at'],format='%m/%d/%y %H:%M')
      df = df.drop(columns=['remove','Lineitem name','Lineitem sku','Created at','Lineitem quantity','Currency'])
      df['Location'] = df['Location'].replace(np.nan, 'Online')

      df['Product(s) Purchased'] = df['Product(s) Purchased'].apply(json.dumps)
      df['Purchase Sku(s)'] = df['Purchase Sku(s)'].apply(json.dumps)

      df.set_index('Name', inplace=True)
      print(list(df.index.names))
      dtype = {'Name':VARCHAR(50)}
      engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root", pw="Crooked31!",db="casca"))
      # Insert whole DataFrame into MySQL
      upsert(engine=engine, df=df, table_name='shopify_data', if_row_exists='update',dtype=dtype)

      #df.to_sql('shopify_data', con = engine, if_exists = 'append', chunksize = 1000, index = False)

@app.route('/uploaded', methods=['GET', 'POST'])
def uploaded_file():
  return '''
  <!doctype html>
  <title>Uploaded the file</title>
  <h1> File has been Successfully Uploaded </h1>
  '''

if (__name__ == "__main__"):
      app.secret_key = 'super secret key'
      app.config['SESSION_TYPE'] = 'filesystem'
      sess = Session()
      sess.init_app(app)
      app.debug = True
      app.run()