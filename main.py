from flask import Flask, render_template, request, flash, redirect, url_for
import os
from os.path import join, dirname, realpath
import os
import datetime
import subprocess
from subprocess import check_output
from werkzeug.utils import secure_filename
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Upload folder

#UPLOAD_FOLDER = 'upload_dir/'
#app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root", pw="Crooked31!",db="csvData"))

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
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('index.html')
    

def parseCSV(filePath):
      # CVS Column Names
      col_names = ['first_name','last_name','address', 'street', 'state' , 'zip']
      # Use Pandas to parse the CSV file
      csvData = pd.read_csv(filePath,names=col_names, header=None)

      # Insert whole DataFrame into MySQL
      csvData.to_sql('addresses', con = engine, if_exists = 'append', chunksize = 1000, index = False)

@app.route('/uploaded', methods=['GET', 'POST'])
def uploaded_file():
  return '''
  <!doctype html>
  <title>Uploaded the file</title>
  <h1> File has been Successfully Uploaded </h1>
  '''

if (__name__ == "__main__"):
     app.run(port = 5000)