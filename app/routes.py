# routes.py
from flask import request, jsonify, current_app as app, redirect, url_for, Response
from flask_login import login_required
import pandas as pd
import os
from .utils import build_hierarchy, convert_booleans_to_strings, refresh_data
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

@app.route('/view_json')
@login_required
def view_json():
    storage_client = storage.Client()
    bucket_name = app.config['GCS_BUCKET_NAME']
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('org_chart.json')

    temp_json_path = '/tmp/org_chart.json'
    try:
        blob.download_to_filename(temp_json_path)
        with open(temp_json_path, 'r') as json_file:
            json_data = json.load(json_file)

        return render_template_with_paths('view_json.html', json_data=json.dumps(json_data, indent=4))
    except Exception as e:
        print(f"Error rendering view_json.html: {e}")
        return str(e)

@app.route('/get_org_chart')
@login_required
def get_org_chart():
    search = request.args.get('search', '').lower()
    show_inactive = request.args.get('showInactive', 'false').lower() == 'true'
    
    print(f"Search term: {search}")
    print(f"Show inactive: {show_inactive}")
    
    storage_client = storage.Client()
    bucket_name = app.config['GCS_BUCKET_NAME']
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('org_chart.json')

    temp_json_path = '/tmp/org_chart.json'
    try:
        blob.download_to_filename(temp_json_path)
        with open(temp_json_path, 'r') as json_file:
            org_chart = json.load(json_file)
        
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
                    print(f"Excluding inactive node: {n['name']}")
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
                print(f"Found node")
                
                filtered_chart = filter_hierarchy(target_node)
                if not filtered_chart:
                    print("No data found after filtering")
                    return jsonify(None)
                
                def count_nodes(node):
                    count = 1  # Count the current node
                    for child in node.get('children', []):
                        count += count_nodes(child)
                    return count
                
                node_count = count_nodes(filtered_chart) - 1  # Exclude the searched node itself
                print(f"Number of nodes attached to the searched node: {node_count}")
                
                return jsonify(filtered_chart)

        print("No matching node found")
        return jsonify(None)
    except Exception as e:
        print(f"Error getting org chart: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/refresh_data')
@login_required
def refresh_data_route():
    try:
        result = refresh_data()
        return jsonify(result)
    except Exception as e:
        print(f"Error refreshing data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
