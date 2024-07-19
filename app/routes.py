from flask import request, jsonify, current_app as app, render_template, redirect, url_for
import pandas as pd
import os
from .utils import build_hierarchy, convert_booleans_to_strings
import json

@app.route('/')
def index():
    print(f"Rendering index.html from: {os.path.join(os.getcwd(), 'templates', 'index.html')}")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        data = pd.read_csv(filepath)
        hierarchy = build_hierarchy(data)
        hierarchy = convert_booleans_to_strings(hierarchy)
        
        json_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'org_chart.json')
        with open(json_filepath, 'w') as json_file:
            json.dump(hierarchy, json_file, indent=4)
        
        return redirect(url_for('view_json'))

@app.route('/view_json')
def view_json():
    json_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'org_chart.json')
    with open(json_filepath, 'r') as json_file:
        json_data = json.load(json_file)
    return render_template('view_json.html', json_data=json_data)
