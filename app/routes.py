# routes.py
from flask import request, jsonify, current_app as app, redirect, url_for, Response, render_template,send_file
from flask_login import login_required
import pandas as pd
import os
from .utils import build_hierarchy, convert_booleans_to_strings, refresh_data,json_to_csv,load_local_json
import json
from google.cloud import storage

def render_template_with_paths(template_name, **context):
    template_path = os.path.join(os.getcwd(), 'templates', template_name)
    css_path = url_for('static', filename='css/styles.css')
    js_path = url_for('static', filename='js/scripts.js')
    print(f"Rendering {template_name} from: {template_path}")
    print(f"CSS path: {css_path}")
    print(f"JS path: {js_path}")
    try:
        with open(template_path) as file:
            content = file.read()
        # Manually inject the paths into the content
        content = content.replace('{{ css_path }}', css_path)
        content = content.replace('{{ js_path }}', js_path)
        for key, value in context.items():
            content = content.replace(f'{{{{ {key} }}}}', value)
        return Response(content, mimetype='text/html')
    except Exception as e:
        print(f"Error rendering {template_name}: {e}")
        return str(e)

@app.route('/')
@app.route('/search')
@app.route('/search/<search_term>')
@login_required
def index(search_term=None):
    return render_template_with_paths('index.html', sign_in_url=url_for('auth.signin'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'recruit_and_recruiter.csv')
        file.save(filepath)
        data = pd.read_csv(filepath)
        hierarchy = build_hierarchy(data)
        hierarchy = convert_booleans_to_strings(hierarchy)
        
        json_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'org_chart.json')
        with open(json_filepath, 'w') as json_file:
            json.dump(hierarchy, json_file, indent=4)
        
        return redirect(url_for('view_json'))

@app.route('/get_org_chart')
@login_required
def get_org_chart():
    search = request.args.get('search', '').lower()
    show_inactive = request.args.get('showInactive', 'false').lower() == 'true'
    
    print(f"Search term: {search}")
    print(f"Show inactive: {show_inactive}")
    
    json_filepath = app.config['LOCAL_JSON_PATH']
    org_chart = load_local_json(json_filepath)
    
    print(f"Org chart loaded")
    
    def find_node(node, search_term):
        if search_term in node['name'].lower():
            return node
        for child in node.get('children', []):
            result = find_node(child, search_term)
            if result:
                return result
        return None

    def filter_hierarchy(node):
        if not node:
            return None

        def filter_chart(n):
            is_active = n['active'] if isinstance(n['active'], bool) else n['active'].lower() == 'true'
            if not show_inactive and not is_active:
                #print(f"Excluding inactive node: {n['name']}")
                return False
            return True

        def apply_filter(n):
            children = n.get('children', [])
            filtered_children = [apply_filter(child) for child in children if filter_chart(child)]
            n['children'] = [child for child in filtered_children if child is not None]
            n['sales'] = n['sales'] + sum(child['sales'] for child in n['children'])
            return n

        return apply_filter(node)

    # Traverse through all nodes starting from each root node
    for root in org_chart['children']:
        target_node = find_node(root, search)
        if target_node:
            #print(f"Found node")
            
            filtered_chart = filter_hierarchy(target_node)
            if not filtered_chart:
                #print("No data found after filtering")
                return jsonify(None)
            
            def count_nodes(node):
                count = 1  # Count the current node
                for child in node.get('children', []):
                    count += count_nodes(child)
                return count
            
            node_count = count_nodes(filtered_chart) - 1  # Exclude the searched node itself
            #print(f"Number of nodes attached to the searched node: {node_count}")
            
            return jsonify(filtered_chart)

    #print("No matching node found")
    return jsonify(None)

@app.route('/refresh_data')
@login_required
def refresh_data_route():
    result = refresh_data()
    return jsonify(result)

@app.route('/get_names')
@login_required
def get_names():
    json_filepath = app.config['LOCAL_JSON_PATH']
    org_chart = load_local_json(json_filepath)
    
    def extract_names(node):
        names = [(node['name'], count_nodes(node))]
        for child in node.get('children', []):
            names.extend(extract_names(child))
        return names

    def count_nodes(node):
        count = 1  # count the current node
        for child in node.get('children', []):
            count += count_nodes(child)
        return count

    all_names = []
    for root in org_chart.get('children', []):
        #print(f"Root node: {root['name']}")
        all_names.extend(extract_names(root))

    #print(f"All names collected: {all_names}")
    return jsonify(all_names)

@app.route('/download_csv', methods=['POST'])
@login_required
def download_csv():
    chart_data = request.json
    if not chart_data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    print('Attemping to download data:')
    print(chart_data)

    # Create a temporary CSV file
    temp_csv_filepath = '/tmp/recruit_and_recruiter.csv'

    if os.path.exists(temp_csv_filepath):
        try:
            os.remove(temp_csv_filepath)
            print('File exists already, removing duplicate.')
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error deleting existing file: {e}"}), 500

    json_to_csv(chart_data, temp_csv_filepath)

    return send_file(temp_csv_filepath, as_attachment=True, download_name='recruit_and_recruiter.csv')