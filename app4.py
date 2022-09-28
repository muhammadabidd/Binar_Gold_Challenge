from fileinput import filename
import re
import sqlite3
import pandas as pd
from flask import Flask, jsonify
import os

from werkzeug.utils import secure_filename

app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app.json_encoder= LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda : 'API Documentation for Data Processing and Modeling'),
    'version': LazyString(lambda : '1.0.0'),
    'description' : LazyString(lambda : 'Dokumentasi API untuk Data Processing dan Modeling'), 
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config = swagger_config)



#Connecting to database
conn = sqlite3.connect('text_processing.db', check_same_thread=False)

#Defining and Executing the Query for table data if it not available
conn.execute('''CREATE TABLE IF NOT EXISTS data (text varchar(255), text_clean varchar(255));''')


@swag_from("docs/hello_world.yml", methods = ['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code' : 200,
        'description': "Menyapa Hello World",
        'data': "Hello World",
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/hello_world.yml", methods = ['GET'])
@app.route('/text', methods=['GET'])
def text():
    json_response = {
        'status_code' : 200,
        'description' : "Original Teks",
        'data' : "Halo, apa kabar semua?",
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/hello_world.yml", methods = ['POST'])
@app.route('/text_clean', methods=['POST'])
def text_clean():
    json_response = {
        'status_code' : 200,
        'description' : "Original Teks",
        'data' : re.sub(r'[^a-zA-Z0-9]', ' ', "Halo, apa kabar semua?)(*)(*()*&"),
    }
    
    response_data = jsonify(json_response)
    return response_data


@swag_from("docs/text_processing.yml", methods = ['POST'])
@app.route('/text_processing', methods=['POST'])
def text_processing():
    text = request.form.get('text')
    text_clean = re.sub(r'[^a-zA-Z0-9]','',text)

    conn.execute("INSERT INTO data(text, text_clean) VALUES ('"+ text +"','"+ text_clean +"')")
    conn.commit()
    conn.close()

    json_response = {
        'status_code' : 200,
        'description' : "Teks yang sudah diproses",
        'data' : text_clean,
    }

    response_data = jsonify(json_response)
    return response_data


## Upload CSV File

#Defining Allowed Extensions
allowed_extensions = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions



@swag_from("docs/file_Upload.yml", methods = ['POST'])
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
   if request.method == 'POST':
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_filename = f'{filename.split(".")[0]}.csv'
            file.save(os.path.join('input', new_filename))
            filepath = 'Input/' + str(new_filename)
            data = pd.read_csv("'" + filepath + "'")
        
            first_column = data.iloc[:, 0]

            for teks in first_column:
                file_clean = re.sub(r'[^a-zA-Z0-9]','',teks)
                conn.execute("INSERT INTO data(text, text_clean) VALUES ('"+ teks +"','"+ file_clean +"')")
        
                print(file_clean)

        conn.commit()
        conn.close()

        json_response = {
            'status_code' : 200,
            'description' : "File yang sudah diproses",
            'data' : data.iloc[:, 1],
        }

        response_data = jsonify(json_response)
        return response_data
    


if __name__ == '__main__' :
    app.run()

