from libs.hyperdb import HyperDB
import json
import pickle

import numpy as np
import api
import sys
np.set_printoptions(threshold=sys.maxsize)
from libs.sql_manager import SQLManager
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Initial data dictionary
data_dict = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

# Function to be called when the button is pushed
def button_pushed():
    global data_dict
    # Update the dictionary (you can modify this logic based on your requirements)
    data_dict['key1'] = 'new_value1'
    data_dict['key2'] = 'new_value2'
    data_dict['key3'] = 'new_value3'

# API endpoint to trigger the button_pushed function
@app.route('/api/button-push', methods=['POST'])
def api_button_push():
    try:
        # Call the button_pushed function
        button_pushed()

        # Return success response
        return jsonify({'status': 'success', 'data_dict': data_dict})

    except Exception as e:
        # Handle errors
        return jsonify({'error': str(e)}), 500


# Web page route to display data from the dictionary
@app.route('/')
def index():
    return render_template('index.html', data_dict=data_dict)

if __name__ == "__main__":
    app.run(debug=True)
  
  